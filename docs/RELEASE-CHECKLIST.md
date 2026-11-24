# Portfolio release checklist

These are review candidates, not production releases. Do not merge, publish or deploy without owner approval.

| Repository | Review acceptance | Remaining limitations |
|---|---|---|
| PID Control Simulator | Analytical tests; manually exercise Streamlit tabs | Sampled margins and Nyquist; separate first-order saturation example |
| Arduino Line Follower | Host tests; Uno compile; inspect physical pinout | PID disabled until hardware calibration and repeatable bench tests |
| SmartPixelProcessor | MATLAB tests; manual load/filter/FFT/save UI exercise | Legacy .mlapp not synchronized; similarity metrics are not quality guarantees |
| EasyCharge | Linux sanitizer tests, Windows build and persistence regressions | Group-atomic persistence and full semantic validation not implemented |
| VOLTEACH | Emulator permissions and authenticated API tests; approved staging | Rotate exposed keys, provision backend, disable unsafe main workflows before PR |
| Private learning project | Parser and timing regressions; private review only | Actual control flow, authentication, data ownership and material rights need review |

Before merging: review full diff, match CI run SHA to branch tip, check licensing and credentials, record owner approval, and decide separately whether a release or deployment is wanted. Never add the private repository or student data to the public profile. Do not claim performance numbers without measurements.
