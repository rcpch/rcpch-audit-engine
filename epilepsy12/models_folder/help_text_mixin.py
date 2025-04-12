from functools import partial as curry


class HelpTextMixin(object):
    """
    Thanks https://bradmontgomery.net/blog/django-hack-help-text-modal-instance/ for this snippet
    Returns the help text methods to the template
    Can use {{first_paediatric_assessment.get_*field*_help_label_text}} and {{first_paediatric_assessment.get_*field*_help_reference_text}}
    in the template
    """

    def _get_help_label_text(self, field_name):
        """Given a field name, return it's label help text."""
        conditional_method = f"get_{field_name}_conditional_help_text"
        if hasattr(self, conditional_method):
            # If we have a conditional help text method, call it
            # and return the result.
            return getattr(self, conditional_method)()["label"]

        # Otherwise, return the default help text.
        # This is the help text that is defined in the model field.
        # It is a dictionary with the keys 'label' and 'reference'.
        # The 'label' key is the label help text and the 'reference' key
        # is the reference help text.
        # We return the label help text.
        for field in self._meta.fields:
            if field.name == field_name:
                return field.help_text["label"]

    def _get_help_reference_text(self, field_name):
        """Given a field name, return it's reference help text."""
        conditional_method = f"get_{field_name}_conditional_help_text"
        if hasattr(self, conditional_method):
            # If we have a conditional help text method, call it
            # and return the result.
            return getattr(self, conditional_method)()["reference"]

        # Otherwise, return the default help text.
        # This is the help text that is defined in the model field.
        # It is a dictionary with the keys 'label' and 'reference'.
        # The 'label' key is the label help text and the 'reference' key
        # is the reference help text.
        for field in self._meta.fields:
            if field.name == field_name:
                return field.help_text["reference"]

    def __init__(self, *args, **kwargs):
        super(HelpTextMixin, self).__init__(*args, **kwargs)
        # Again, iterate over all of our field objects.
        for field in self._meta.fields:
            # Create a string, get_FIELDNAME_help text
            label_method_name = "get_{0}_help_label_text".format(field.name)
            reference_method_name = "get_{0}_help_reference_text".format(field.name)

            # We can use curry to create the method with a pre-defined argument
            label_curried_method = curry(
                self._get_help_label_text, field_name=field.name
            )
            reference_curried_method = curry(
                self._get_help_reference_text, field_name=field.name
            )

            # And we add this method to the instance of the class.
            setattr(self, label_method_name, label_curried_method)
            setattr(self, reference_method_name, reference_curried_method)

    class Meta:
        abstract = True
