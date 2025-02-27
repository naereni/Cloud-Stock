from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe


class CustomClearableFileInput(ClearableFileInput):
    template_name = "your_template.html"

    def __init__(self, *args, clear_checkbox_label=None, **kwargs):
        self.clear_checkbox_label = clear_checkbox_label or ""
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Убираем отображение чекбокса и надписи
        context["widget"]["clear_checkbox_label"] = ""
        context["widget"]["clear_checkbox_name"] = ""
        context["widget"]["is_initial"] = False
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        # Ваш код для кастомного рендеринга без чекбокса и надписи
        return mark_safe('<input type="file" name="{}" class="{}">'.format(name, self.attrs.get("class", "")))
