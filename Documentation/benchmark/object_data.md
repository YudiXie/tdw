# Object data

Collecting object data in TDW is _very_ fast. This benchmark measures the performance of each standard type of object data.

See [the Benchmark document](benchmark.md) for the test machine's system info.

In each test, there are 100 objects in the scene. There is no camera or image data.

| Transforms | Rigidbodies | Bounds | Collisions | FPS  |
| ---------- | ----------- | ------ | ---------- | ---- |
| True       | False       | False  | False      | 683  |
| False      | True        | False  | False      | 703  |
| False      | False       | True   | False      | 411  |
| False      | False       | False  | True       | 594  |
| True       | True        | True   | True       | 312  |

## How to run TDW's image capture performance benchmarks

1. [Follow instructions in the Benchmark document for cloning the repo, downloading the build, etc.](benchmark.md)
2. `cd path/to/tdw/Python/benchmarking` (replace `path/to` with the actual path)
3. `python3 object_data.py`
4. Run the build
5. Wait for the performance benchmark to complete (this might take up to five minutes).
6. Compare your results to those listed above

***

**Next: [Command deserialization](command_deserialization.md)**

[Return to the README](../../README.md)
