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
