from primehub.admin_instancetypes import validate, required_field, \
    required_numeric_field, required_gt_0, validate_cpu_fields, validate_memory_fields, validate_gpu_field, \
    required_int_field, validate_tolerations_field, TOLERATION_FORMAT_ERROR, required_str_lengths_3_63, \
    TOLERATION_OPERATOR_ERROR, TOLERATION_EQUAL_OPERATOR_ERROR, TOLERATION_EXISTS_OPERATOR_ERROR, \
    TOLERATION_EFFECT_ERROR, \
    validate_node_selector_field, NODE_SELECTOR_FORMAT_ERROR, NODE_SELECTOR_KV_TYPE_ERROR, NODE_SELECTOR_KEY_LEN_ERROR
from primehub.utils import PrimeHubException
from tests import BaseTestCase


class TestAdminInstanceTypes(BaseTestCase):

    def setUp(self) -> None:
        super(TestAdminInstanceTypes, self).setUp()

    def check_required(self, cfg: dict, message: str, callback=None):
        with self.assertRaises(PrimeHubException) as context:
            if callback is None:
                validate(cfg)
            else:
                callback(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def check_cpu_fields(self, cfg: dict, message: str):
        self.check_required(cfg, message, validate_cpu_fields)

    def check_memory_fields(self, cfg: dict, message: str):
        self.check_required(cfg, message, validate_memory_fields)

    def check_gpu_field(self, cfg: dict, message: str):
        self.check_required(cfg, message, validate_gpu_field)

    def check_tolerations_field(self, cfg: dict, message: str):
        self.check_required(cfg, message, validate_tolerations_field)

    def check_node_selector_field(self, cfg: dict, message: str):
        self.check_required(cfg, message, validate_node_selector_field)

    def test_basic_fields_validator(self):
        # check empty config, required name
        payload = {}
        self.check_required(payload, 'name is required')

    def test_gpu_field_validator(self):
        # check with bad gpu limit: float value
        payload = {'gpuLimit': 0.5}
        self.check_gpu_field(payload, required_int_field('gpuLimit'))

        # check with bad gpu limit: < 0
        payload = {'gpuLimit': -1}
        self.check_gpu_field(payload, required_gt_0('gpuLimit'))

        # pass without gpu limit
        validate_gpu_field({})

        # pass with valid gpu limit
        validate_gpu_field({'gpuLimit': 1})

    def test_cpu_fields_validator(self):

        # check without cpu limit
        payload = {}
        self.check_cpu_fields(payload, required_field('cpuLimit'))

        # check with bad cpu limit <str>
        payload = {'cpuLimit': '1'}
        self.check_cpu_fields(payload, required_numeric_field('cpuLimit'))

        # check with bad cpu limit < 1
        payload = {'cpuLimit': -1}
        self.check_cpu_fields(payload, required_gt_0('cpuLimit'))

        payload = {'cpuLimit': 0}
        self.check_cpu_fields(payload, required_gt_0('cpuLimit'))

        # check with bad cpu request <str>
        payload = {'cpuLimit': 1, 'cpuRequest': '1'}
        self.check_cpu_fields(payload, required_numeric_field('cpuRequest'))

        # check with bad cpu request > cpu limit
        payload = {'cpuLimit': 1, 'cpuRequest': 2}
        self.check_cpu_fields(payload, 'cpuRequest should less or equal to cpuLimit')

        # pass with cpuLimit == cpuRequest
        payload = {'cpuLimit': 1, 'cpuRequest': 1}
        validate_cpu_fields(payload)

        # pass with cpuLimit > cpuRequest
        payload = {'cpuLimit': 1.5, 'cpuRequest': 1}
        validate_cpu_fields(payload)

        # pass with cpuLimit only
        payload = {'cpuLimit': 1.5}
        validate_cpu_fields(payload)

    def test_memory_fields_validator(self):

        # check without memory limit
        payload = {}
        self.check_memory_fields(payload, required_field('memoryLimit'))

        # check with bad memory limit <str>
        payload = {'memoryLimit': '1'}
        self.check_memory_fields(payload, required_numeric_field('memoryLimit'))

        # check with bad memory limit < 1
        payload = {'memoryLimit': -1}
        self.check_memory_fields(payload, required_gt_0('memoryLimit'))

        payload = {'memoryLimit': 0}
        self.check_memory_fields(payload, required_gt_0('memoryLimit'))

        # check with bad memory request <str>
        payload = {'memoryLimit': 1, 'memoryRequest': '1'}
        self.check_memory_fields(payload, required_numeric_field('memoryRequest'))

        # check with bad memory request > memory limit
        payload = {'memoryLimit': 1, 'memoryRequest': 2}
        self.check_memory_fields(payload, 'memoryRequest should less or equal to memoryLimit')

        # pass with memoryLimit == memoryRequest
        payload = {'memoryLimit': 1, 'memoryRequest': 1}
        validate_memory_fields(payload)

        # pass with memoryLimit > memoryRequest
        payload = {'memoryLimit': 1.5, 'memoryRequest': 1}
        validate_memory_fields(payload)

        # pass with memoryLimit only
        payload = {'memoryLimit': 2.5}
        validate_memory_fields(payload)

    def test_tolerations_field_validator(self):

        # check tolerations with wrong format
        payload = {'tolerations': {'unset': []}}
        self.check_tolerations_field(payload, TOLERATION_FORMAT_ERROR)

        payload = {'tolerations': {'unset': [], 'set': []}}
        self.check_tolerations_field(payload, TOLERATION_FORMAT_ERROR)

        def t(toleration: dict):
            return {'tolerations': {'set': [toleration]}}

        # check invalid operator
        payload = t(dict(key='key1', value='value1', operator=''))
        self.check_tolerations_field(payload, TOLERATION_OPERATOR_ERROR)

        # check invalid operator: equal should go with `value`
        payload = t(dict(key='keyEquals', operator='Equal'))
        self.check_tolerations_field(payload, TOLERATION_EQUAL_OPERATOR_ERROR)

        # check invalid operator: exists should not go with `value`
        payload = t(dict(key='key2', value='value2', operator='Exists'))
        self.check_tolerations_field(payload, TOLERATION_EXISTS_OPERATOR_ERROR)

        # check with key length not between 3 and 63
        payload = t(dict(key='a', value='b'))
        self.check_tolerations_field(payload, required_str_lengths_3_63('key'))

        # check with value length not between 3 and 63
        payload = t(dict(key='my-key', value='b', operator='Equal'))
        self.check_tolerations_field(payload, required_str_lengths_3_63('value'))

        # check invalid effect: effect could be empty or one of the {NoSchedule, PreferNoSchedule and NoExecute}
        payload = t(dict(key='key2', value='value2', operator='Equal', effect='PrimeHub'))
        self.check_tolerations_field(payload, TOLERATION_EFFECT_ERROR)

        # pass with valid setting: Equal operator
        payload = t(dict(key='key2', value='value2', operator='Equal', effect='NoSchedule'))
        validate_tolerations_field(payload)

        # pass with valid setting: Exists operator
        payload = t(dict(key='key2', operator='Exists'))
        validate_tolerations_field(payload)

        # pass with valid format
        payload = {'tolerations': {'set': []}}
        validate_tolerations_field(payload)

        # pass no tolerations
        validate_tolerations_field({})

    def test_node_selector_field_validator(self):

        def n(selectors: dict):
            return {'nodeSelector': {**selectors}}

        # type checking
        self.check_node_selector_field({'nodeSelector': []}, NODE_SELECTOR_FORMAT_ERROR)
        self.check_node_selector_field(n(dict(key=1)), NODE_SELECTOR_KV_TYPE_ERROR)
        self.check_node_selector_field(n(dict(key=None)), NODE_SELECTOR_KV_TYPE_ERROR)
        self.check_node_selector_field(n({1: "value"}), NODE_SELECTOR_KV_TYPE_ERROR)

        # check key length > 63
        self.check_node_selector_field(n({"k" * 64: "value"}), NODE_SELECTOR_KEY_LEN_ERROR)

        # pass with valid content
        validate_node_selector_field(n(dict(key1='value1', key2='value2')))
        validate_node_selector_field(n({"k" * 63: "value"}))

        # pass without node selector
        validate_node_selector_field({})

        # pass with empty node selector
        validate_node_selector_field({'nodeSelector': {}})
