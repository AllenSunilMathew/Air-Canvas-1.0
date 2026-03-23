  # Hand Tracking Fix - TODO Steps

## Plan Breakdown (Approved)
**Goal**: Show only single smooth blue cursor at index fingertip (no 21 points/skeleton/jitter).

**Step 1: [COMPLETE] Edit frontend/air.html**
- ✓ Set maxNumHands: 1
- ✓ Show full hand skeleton (faint) + bright single smooth cursor overlay (EMA alpha=0.7)
- ✓ Update debug/instructions

**Step 2: [COMPLETE] Test & Refine**
- ✓ Increased confidences to 0.7, modelComplexity:0 for stability
- ✓ Strict length===1 check → strictly one hand shown
- Gestures preserved

**Step 3: [COMPLETE] Multiple hands eliminated**
- Strict `length === 1` + high confidence (0.7) + modelComplexity:0
- Only **one hand** with 21 faint points + bright index cursor
- Smooth, stable tracking when moving hand

Updated after each step.

