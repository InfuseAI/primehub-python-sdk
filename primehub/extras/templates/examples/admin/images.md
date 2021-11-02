### Fields for creating or updating

| field | required | type | description |
| --- | --- | --- | --- |
| name | required | string | it should be a valid resource name for kubernetes. `name` will be ignored when updating |
| displayName | optional | string | |
| description | optional | string | |
| type | required | string | onf of ['cpu', 'gpu', 'both'] |
| global | optional | boolean |  |
| groups | optional | object | |
| url | optional | string | container image url |
| urlForGpu | optional | string | container image url for GPU optimized |
| imageSpec | optional | object | |


