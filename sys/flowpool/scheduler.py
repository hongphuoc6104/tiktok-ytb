"""Pure scheduling decisions (no I/O), so they can be tested exhaustively.

Images: round-robin over free ready profiles. A profile with a B-2 tool
remix and media IDs for every reference takes up to one B-2 queue (<=4);
otherwise the image goes through the plain Flow UI, one per submission.
Clips: the free ready profile with the most credits left this month (the
lower of the UI balance and its monthly cap minus ledger spend; unknown ranks
last), one clip submission at a time.
"""
import math

IMAGE_STATES = ('ready', 'low_credit')  # images have shown no credit charge (22/09 measurement)
CLIP_STATES = ('ready',)
TRANSIENT = ('busy', 'cooldown')


class Context:
    """Facts the scheduler needs: per-profile media IDs and clip cost."""

    def __init__(self, cfg, media_lookup=None, clip_cost=None, remaining=None):
        self.cfg = cfg
        self.media_lookup = media_lookup or {}
        self.clip_cost = clip_cost or (lambda model: cfg.get('flowpool_clip_credit_estimate', {}).get(model, 0))
        # Credits this profile may still spend this month (None = unknown).
        self.remaining = remaining or (lambda profile: profile.get('credits'))

    def media_id(self, profile, sha):
        return (profile.get('media_ids') or {}).get(sha) or self.media_lookup.get(sha, {}).get(profile['name'])

    def cost(self, req):
        if req['kind'] != 'clip':
            return 0
        return self.clip_cost(req.get('model')) * int(req.get('variants') or 1)


def engine(profile, req, ctx):
    """'b2' (remixed queue tool, needs account media IDs), 'flow' (plain Flow UI) or 'clip'."""
    if req['kind'] == 'clip':
        return 'clip'
    if req.get('purpose') == 'mascot_bootstrap':
        return 'flow'
    if (profile.get('tool_url') and int(req.get('variants') or 1) == 1
            and req.get('_ref_shas')
            and all(ctx.media_id(profile, sha) for sha in req['_ref_shas'])):
        return 'b2'
    return 'flow'


def eligible(profile, req, ctx, states=None):
    """(ok, reason). `states` overrides the accepted profile states."""
    if not profile.get('enabled'):
        return False, 'disabled'
    kind = req['kind']
    allowed = states or (IMAGE_STATES if kind == 'image' else CLIP_STATES)
    if profile.get('state') not in allowed:
        return False, profile.get('state')
    if kind == 'image':
        return True, None
    left = ctx.remaining(profile)
    if left is not None and left < ctx.cost(req):
        return False, 'insufficient_credits'
    return True, None


def can_ever_run(req, profiles, ctx):
    """True when some enabled, non-blocked profile could take the request once free."""
    states = (IMAGE_STATES if req['kind'] == 'image' else CLIP_STATES) + TRANSIENT
    return any(eligible(p, req, ctx, states)[0] for p in profiles)


def next_batch(pending, profiles, ctx, busy=(), slots=1, rr=None, cap=4):
    """Pick (profile, batch) for one free slot, or None.

    `rr` is a one-element list carrying the round-robin cursor (last priority used).
    """
    rr = rr if rr is not None else [-1]
    free = [p for p in profiles if p['name'] not in busy]
    for req in pending:
        cands = sorted((p for p in free if eligible(p, req, ctx)[0]), key=lambda p: p.get('priority', 0))
        if not cands:
            continue
        if req['kind'] == 'clip':
            best = max(cands, key=lambda p: (ctx.remaining(p) is not None, ctx.remaining(p) or 0, -p.get('priority', 0)))
            return best, [req]
        after = [p for p in cands if p.get('priority', 0) > rr[0]]
        chosen = (after or cands)[0]
        rr[0] = chosen.get('priority', 0)
        how = engine(chosen, req, ctx)
        if how != 'b2':
            return chosen, [req]
        limit = min(cap, int(chosen.get('max_parallel') or cap))
        images = [r for r in pending if r['kind'] == 'image' and r.get('model') == req.get('model')
                  and eligible(chosen, r, ctx)[0] and engine(chosen, r, ctx) == 'b2']
        share = math.ceil(len(images) / max(1, min(len(cands), max(1, slots))))
        size = max(1, min(limit, share))
        batch = [req] + [r for r in images if r is not req][:size - 1]
        return chosen, batch
    return None
