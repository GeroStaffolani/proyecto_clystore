def user_info(request):
    """
    Context processor para agregar información del usuario a todos los templates
    """
    context = {}
    if request.user.is_authenticated:
        context['user_role'] = 'admin' if request.user.is_staff else 'empleado'
        context['user_full_name'] = request.user.get_full_name() or request.user.username
    return context
