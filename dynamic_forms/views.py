import json
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models

from content_type_constants import get_content_type_for_model, ORDER_CT_CACHE_KEY
from dynamic_forms.models import FormField, FormFieldPermission
from dynamic_forms.forms import FormFieldForm
from orders.models import Order
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product, Material, MaterialCategory
from accounting.models import PaymentMethod
from constants import USER_TYPE_CHOICES, PERMISSION_CHOICES


class AdminFormFieldMixin(object):
    model = FormField
    context_object_name = "form_fields"
    success_url = reverse_lazy("sales_funnel:admin_funnel_list")

    def get_queryset(self):
        order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
        user = self.request.user
        return (
            self.model.objects.filter(company=user.company, content_type=order_ct)
            .select_related('associated_blocking_field', 'associated_content_type')
            .all()
            .order_by("sorting")
        )


class AdminFormFieldListView(AdminFormFieldMixin, ListView):
    template_name = "dynamic_forms/admin_form_field/list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
        context['existing_fields'] = FormField.objects.filter(
            company=self.request.user.company,
            content_type=order_ct
        ).values('id', 'label', 'name')
        
        # Get available content types for associated objects
        context['available_content_types'] = ContentType.objects.filter(
            model__in=['formfield', 'product', 'material', 'materialcategory', 'paymentmethod']
        ).order_by('model')
        
        # Add user types and permissions for permissions section
        context['user_types'] = USER_TYPE_CHOICES
        context['permission_choices'] = PERMISSION_CHOICES
        
        return context


class SortFormFieldUpdateView(View):
    def post(self, request):
        sorted_form_fields = json.loads(request.POST.get("sorted_form_fields", "[]"))
        for index, form_field_id in enumerate(sorted_form_fields):
            funnel = FormField.objects.get(id=int(form_field_id))
            funnel.sorting = index
            funnel.save()
        return JsonResponse({"success": True})


class AdminFormFieldCreateView(LoginRequiredMixin, CreateView):
    """
    AJAX view for creating new FormField instances
    """
    model = FormField
    form_class = FormFieldForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
        kwargs['content_type'] = order_ct
        return kwargs
    
    def form_valid(self, form):
        instance = form.save()
        
        # Set sorting to max + 1 if not provided or 0
        if instance.sorting == 0:
            order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
            max_sorting = FormField.objects.filter(
                company=instance.company,
                content_type=order_ct
            ).aggregate(models.Max('sorting'))['sorting__max'] or 0
            instance.sorting = max_sorting + 1
            instance.save()
        
        # Create FormFieldPermission objects from form data
        permissions_data = self.request.POST.get('permissions', '{}')
        if permissions_data:
            try:
                permissions_dict = json.loads(permissions_data)
                for user_type_str, permission in permissions_dict.items():
                    if permission:  # Only create if permission is selected
                        user_type = int(user_type_str)
                        FormFieldPermission.objects.create(
                            form_field=instance,
                            user_type=user_type,
                            permission=permission,
                            sorting=0
                        )
            except (json.JSONDecodeError, ValueError):
                # Log error but don't fail the request
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Field created successfully',
            'field': {
                'id': instance.id,
                'label': instance.label,
                'name': instance.name,
                'field_type': instance.get_field_type_display(),
                'is_required': instance.is_required,
            }
        })
    
    def form_invalid(self, form):
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [str(error) for error in error_list]
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)


class AdminFormFieldDeleteView(LoginRequiredMixin, View):
    """
    AJAX view for deleting FormField instances
    """
    def post(self, request):
        field_id = request.POST.get('field_id')
        try:
            field = FormField.objects.get(
                id=field_id, 
                company=request.user.company
            )
            field.delete()
            return JsonResponse({
                'success': True,
                'message': 'Field deleted successfully'
            })
        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Field not found'
            }, status=404)


class GetAssociatedObjectsView(LoginRequiredMixin, View):
    """
    AJAX view for getting list of objects for selected Content Type
    """
    def get(self, request):
        content_type_id = request.GET.get('content_type_id')
        if not content_type_id:
            return JsonResponse({'success': False, 'message': 'Content type ID is required'}, status=400)
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model_class = content_type.model_class()
            company = request.user.company
            
            # Get objects based on model type
            objects = []
            
            if model_class == FormField:
                order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
                queryset = FormField.objects.filter(
                    company=company,
                    content_type=order_ct
                )
                objects = [{'id': obj.id, 'name': f'{obj.label} ({obj.name})'} for obj in queryset]
            
            elif model_class == Product:
                queryset = Product.objects.filter(company=company)
                objects = [{'id': obj.id, 'name': obj.title} for obj in queryset]
            
            elif model_class == Material:
                # Materials are filtered by category, but we'll show all for company
                queryset = Material.objects.filter(category__company=company)
                objects = [{'id': obj.id, 'name': f'{obj.title} ({obj.category.title})'} for obj in queryset]
            
            elif model_class == MaterialCategory:
                queryset = MaterialCategory.objects.filter(company=company)  # type: ignore
                objects = [{'id': obj.id, 'name': obj.title} for obj in queryset]
            
            elif model_class == PaymentMethod:
                queryset = PaymentMethod.objects.filter(company=company)
                objects = [{'id': obj.id, 'name': obj.title} for obj in queryset]
            
            else:
                # Generic fallback - try to filter by company if model has company field
                try:
                    queryset = model_class.objects.all()
                    if hasattr(model_class, 'company'):
                        queryset = queryset.filter(company=company)
                    objects = [{'id': obj.id, 'name': str(obj)} for obj in queryset[:100]]  # Limit to 100
                except:
                    objects = []
            
            return JsonResponse({
                'success': True,
                'objects': objects
            })
            
        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Content type not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
