/** Fail-closed guards around pinned gflow 1.1.1; never alter node_modules. */
import {readFileSync, writeFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = join(root, 'node_modules/@swissmarley/gflow-cli');
if (JSON.parse(readFileSync(join(base,'package.json'))).version !== '1.1.1') throw Error('Pinned gflow version mismatch');
const {FlowPage} = await import(join(base,'dist/src/flow/page.js'));
const {CharacterPage} = await import(join(base,'dist/src/flow/characters.js'));
const {flowLocators} = await import(join(base,'dist/src/flow/locators.js'));
const {dismissOpenLayers} = await import(join(base,'dist/src/flow/ui.js'));
const {runCli} = await import(join(base,'dist/src/cli.js'));
const args = process.argv.slice(2);
const image = args[0] === 'image';
const character = args[0] === 'character' && args[1] === 'create';
if (!image && !character) throw Error('M2_POLICY: only image or character create allowed');
const out = args[args.indexOf('--out')+1];
if (!out || !args.includes('--out')) throw Error('Output directory required');
const evidenceDir = dirname(out);
const proof = {mode: image ? 'image' : 'character-register', characters: [], passed: false};
const originalSettings = FlowPage.prototype.applySettings;
FlowPage.prototype.applySettings = async function(job) {
  if(job.type !== 'image' || job.ratio !== '9:16' || job.outputs !== 1) throw Error('Image pilot settings required');
  await originalSettings.call(this,job);
  const settings = flowLocators(this.page).settingsButton.first();
  await settings.waitFor({state:'visible'});
  const label = await settings.innerText();
  if (!label.includes(job.model) || !label.includes('crop_9_16')) throw Error('Cannot verify model/portrait settings');
  await settings.click();
  const selected = this.page.locator('[aria-selected="true"], [aria-pressed="true"], [data-state="active"], [data-state="checked"]');
  const labels = await selected.allTextContents();
  if (!labels.some(x => /(?:^|\s)Image\s*$/.test(x.trim()))) throw Error('Cannot verify selected IMAGE mode; stopped before submit');
  proof.settings = {label,selected:labels};
  await dismissOpenLayers(this.page);
};
FlowPage.prototype.referenceCharacter = async function(name) {
  const add = this.page.locator('button[aria-haspopup="dialog"]').filter({hasText:/add_2/}).first();
  await add.click();
  const dialog = this.page.locator('[role="dialog"],[aria-modal="true"]').first();
  await dialog.waitFor({state:'visible'});
  await dialog.locator('button,[role=tab]').filter({hasText:/Characters/i}).first().click();
  await dialog.getByText(name,{exact:true}).first().click();
  await dialog.locator('button').filter({hasText:/add to prompt/i}).first().click();
  await dialog.waitFor({state:'hidden'});
  // Must see the attached name after the picker is closed; absence is a hard failure.
  await this.page.getByText(name,{exact:true}).first().waitFor({state:'visible'});
  proof.characters.push(name);
};
const originalSubmit = FlowPage.prototype.submit;
FlowPage.prototype.submit = async function() {
  if (!proof.settings) throw Error('IMAGE mode evidence missing');
  await this.page.screenshot({path:join(evidenceDir,'before-submit.png')});
  proof.passed=true;proof.flow_url=this.page.url();
  writeFileSync(join(evidenceDir,'ui-proof.json'),JSON.stringify(proof,null,2));
  return originalSubmit.call(this);
};
const originalCharacterCheck = CharacterPage.prototype.assertNotBlocked;
CharacterPage.prototype.assertNotBlocked = async function() {
  await originalCharacterCheck.call(this);
  if (!/\/characters(?:[/?#]|$)/.test(this.page.url())) throw Error('Character page not verified');
  await this.page.screenshot({path:join(evidenceDir,'before-submit.png')});
  proof.passed=true;proof.flow_url=this.page.url();
  writeFileSync(join(evidenceDir,'ui-proof.json'),JSON.stringify(proof,null,2));
};
process.exitCode = await runCli(['node','gflow',...args]);
