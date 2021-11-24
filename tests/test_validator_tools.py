import json
from unittest import TestCase

from primehub import PrimeHubException
from primehub.utils.validator import ValidationSpec


class TestValidatorTools(TestCase):

    def setUp(self) -> None:
        super(TestValidatorTools, self).setUp()

    def got_failed(self, spec: ValidationSpec, cfg: dict, message: str):
        with self.assertRaises(PrimeHubException) as context:
            spec.validate(cfg)

        self.assertTrue(isinstance(context.exception, PrimeHubException))
        self.assertEqual(message, context.exception.args[0])

    def test_validator(self):

        spec = ValidationSpec(
            """
            id: ID!
            string_field: String
            number: Int
            float: Float
            object: JSON
            """
        )

        def type_error(field: str, type_class_list: list):
            if not isinstance(type_class_list, list):
                return f'The value of the {field} should be the {type_class_list.__name__} type'
            if len(type_class_list) == 1:
                return f'The value of the {field} should be the {type_class_list[0].__name__} type'
            types = ", ".join([x.__name__ for x in type_class_list])
            return f'The value of the {field} should be one of the types: [{types}]'

        def _f(field: str, value):
            return {'id': 'id', **{field: value}}

        test_examples = [(int, 1), (float, 1.4), (bool, True), (bool, False), (str, ''), (str, 'string'),
                         (dict, {'v': 2}), (tuple, (1, 2, 3,))]

        def bad_examples(excludes: list):
            return [x for x in test_examples if x[0] not in excludes]

        def good_examples(includes: list):
            return [x for x in test_examples if x[0] in includes]

        def general_type_tester(spec, type_class, field_name):
            print(f'General_type_tester {"::" * 30} type[{type_class}] <== {field_name}  ')

            type_list = type_class
            if not isinstance(type_list, list):
                type_list = [type_list]

            for ex in bad_examples(type_list):
                # ex => {type_class, type_example}
                print(f'check bad examples: {ex} => {_f(field_name, ex[1])}')
                self.got_failed(spec, _f(field_name, ex[1]), type_error(field_name, type_list))
            for ex in good_examples(type_list):
                # ex => {type_class, type_example}
                print(f'check good examples: {ex} => {_f(field_name, ex[1])}')
                spec.validate(_f(field_name, ex[1]))

        # check ID!
        self.got_failed(spec, {'id': None}, 'id can not be null, it is a required field')
        self.got_failed(spec, {'id': 123}, type_error('id', str))
        self.got_failed(spec, {'id': 5.5}, type_error('id', str))
        self.got_failed(spec, {'id': True}, type_error('id', str))

        # check String field
        general_type_tester(spec, str, 'string_field')

        # check Int field
        general_type_tester(spec, int, 'number')

        # check JSON field
        general_type_tester(spec, dict, 'object')

        # check float field
        general_type_tester(spec, [int, float], 'float')

    def test_validation_optional_fields_will_skip(self):
        spec = ValidationSpec(
            """
            str: String
            int: Int
            float: Float
            dict: JSON
            """
        )

        # pass with nothing with the data
        spec.validate({})

        # pass with None (skip to check None values)
        spec.validate({'str': None})
        spec.validate({'int': None})
        spec.validate({'float': None})
        spec.validate({'dict': None})

    def test_multi_rules(self):
        from primehub.utils.validator import Validator

        class OpC8763(Validator.OpBase):
            def __init__(self):
                super().__init__([str])

            def validate(self, value):
                if not super(OpC8763, self).validate(value):
                    return False
                return 'C8763' in value

            def error_message(self, field: str):
                return f'The value of the {field} should contain "C8763"'

        class OpParsedJson(Validator.OpBase):
            def __init__(self):
                super().__init__([str])

            def validate(self, value):
                if not super(OpParsedJson, self).validate(value):
                    return False
                try:
                    json.loads(value)
                    return True
                except BaseException:
                    return False

            def error_message(self, field: str):
                return f'The value of the {field} should be a valid json string'

        # register validation operators
        Validator.OpC8763 = OpC8763
        Validator.OpParsedJson = OpParsedJson

        spec = ValidationSpec(
            """
            foo:String
            foo:C8763
            """
        )
        self.got_failed(spec, dict(foo=1), 'The value of the foo should be the str type')
        self.got_failed(spec, dict(foo=''), 'The value of the foo should contain "C8763"')
        spec.validate(dict(foo='... C8763 ...'))

        spec = ValidationSpec(
            """
            foo:C8763
            foo:ParsedJson
            """
        )
        self.got_failed(spec, dict(foo='C8763'), 'The value of the foo should be a valid json string')
        spec.validate(dict(foo='["C8763"]'))
        spec.validate(dict(foo='{"name": "skill", "value": "C8763"}'))

    def test_phjob_create_input(self):
        spec = ValidationSpec("""
        input PhJobCreateInput {
          displayName: String!
          groupId: String!
          instanceType: String!
          image: String!
          command: String!
          activeDeadlineSeconds: IntGe0
        }
        """)

        data = {}
        self.got_failed(spec, data, 'displayName is a required field')

        data['displayName'] = True
        self.got_failed(spec, data, 'The value of the displayName should be the str type')

        data['displayName'] = 'my-job'
        self.got_failed(spec, data, 'groupId is a required field')

        data['groupId'] = 'group-id'
        self.got_failed(spec, data, 'instanceType is a required field')

        data['instanceType'] = 'instance-type'
        self.got_failed(spec, data, 'image is a required field')

        data['image'] = 'image'
        self.got_failed(spec, data, 'command is a required field')

        data['command'] = 'date'

        # We have all required fields
        spec.validate(data)

        # Check activeDeadlineSeconds
        data['activeDeadlineSeconds'] = None
        spec.validate(data)

        data['activeDeadlineSeconds'] = 1.5
        self.got_failed(spec, data, 'The value of the activeDeadlineSeconds should be an integer value >= 0')

        data['activeDeadlineSeconds'] = -1
        self.got_failed(spec, data, 'The value of the activeDeadlineSeconds should be an integer value >= 0')

        data['activeDeadlineSeconds'] = 0
        spec.validate(data)
