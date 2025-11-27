from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def split(value, delimiter=','):
    """Divide una cadena por el delimitador especificado."""
    if value:
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    return []

@register.filter
def trim(value):
    """Elimina espacios en blanco al inicio y final."""
    if value:
        return value.strip()
    return value 

@register.filter
def cop_currency(value):
    """Formatea un número como moneda colombiana."""
    try:
        # Convertir a float y formatear con separadores de miles
        number = float(value)
        formatted = f"${number:,.0f} COP"
        return formatted
    except (ValueError, TypeError):
        return value

@register.filter
def get_other_user(connection, current_user):
    """Obtiene el otro usuario en una conexión mentor-inversionista."""
    if hasattr(connection, 'get_other_user'):
        return connection.get_other_user(current_user)
    return None

@register.filter
def has_profile(user):
    """Verifica si el usuario tiene un perfil asociado."""
    return hasattr(user, 'profile') and user.profile is not None

@register.filter
def get_user_type(user):
    """Obtiene el tipo de usuario de forma segura."""
    if hasattr(user, 'profile') and user.profile:
        return user.profile.user_type
    return None