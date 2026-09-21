#!/usr/bin/env python3
"""Export measured rates from an approved media job, never mutate saved briefs."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot, Blocked, write
import workflow
from scripts.story_plan import calibrate_rates

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('job');parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    p=Pilot()
    try:
        p.status(args.job)
        if not workflow.approved(p,args.job,'media'): raise Blocked('Media must be approved before calibration')
        output=args.output.resolve()
        if output.is_relative_to((p.root/'runs').resolve()) or output.exists():
            raise Blocked('Use a new output file outside saved job history')
        value=calibrate_rates(p.payload(args.job,'content'),p.payload(args.job,'audio'),
                              args.job+' audio hash '+p.rows(args.job)['audio']['hash'])
        write(output,value)
        print(output)
    finally:p.db.close()
if __name__=='__main__':main()
