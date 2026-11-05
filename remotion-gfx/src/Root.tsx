import React from 'react';
import {Composition} from 'remotion';
import {LoanMeter} from './LoanMeter';
import {RebateRing} from './RebateRing';
import {LocationPin} from './LocationPin';
export const Root: React.FC = () => (
  <>
    <Composition id="LoanMeter" component={LoanMeter} width={600} height={190} fps={30} durationInFrames={210} />
    <Composition id="RebateRing" component={RebateRing} width={300} height={330} fps={30} durationInFrames={120} />
    <Composition id="LocationPin" component={LocationPin} width={640} height={200} fps={30} durationInFrames={120} />
  </>
);
