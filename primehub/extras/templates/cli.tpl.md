
# Primehub {{command.capitalize()}}

```
{{command_help}}
```

{% for item in actions %}
### {{item['name']}}

{{item['description']}}

{% if item['required_arguments'] %}
```
primehub {{command}} {{item['name']}} {{item['required_arguments_string']}}
```
{% else %}
```
primehub {{command}} {{item['name']}}
```
{% endif %}

{%- if item['required_arguments'] -%}
{%- for argument in item['required_arguments'] %}
* {{argument}}
{%- endfor %}
{% endif %} {# end of :: if item['required_arguments'] #}
{% for argument in item['optional_arguments'] %}
* *(optional)* {{argument}}
{% endfor %}


{% endfor %} {# end of :: for item in actions #}

