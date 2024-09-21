from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms import widgets

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, displaying a list of checkboxes.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RestaurantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    categories = MultiCheckboxField('Categories', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
