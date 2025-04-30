from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import JsonResponse

from core.models import Student, User

@login_required
@user_passes_test(lambda u: u.is_superuser)
def remove_fifth_year_students(request):
    """View to find and remove 5th year students from the system"""
    
    # Find all 5th year students
    fifth_year_students = Student.objects.filter(year_level=5).select_related('user', 'course')
    count = fifth_year_students.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_all':
            # Delete all 5th year students
            deleted_count = 0
            for student in fifth_year_students:
                try:
                    # Get the user associated with the student
                    user = student.user
                    student_name = f"{user.first_name} {user.last_name}"
                    # Delete the user which will cascade delete the student
                    user.delete()
                    deleted_count += 1
                except Exception as e:
                    messages.error(request, f"Error deleting student: {str(e)}")
            
            messages.success(request, f"Successfully deleted {deleted_count} 5th year students.")
            return redirect('admin_students')
        
        elif action == 'delete_selected':
            # Delete selected students
            selected_students = request.POST.getlist('selected_students')
            if not selected_students:
                messages.error(request, "No students selected for deletion.")
                return redirect('remove_fifth_year_students')
            
            deleted_count = 0
            for student_id in selected_students:
                try:
                    student = Student.objects.get(id=student_id)
                    student_name = f"{student.user.first_name} {student.user.last_name}"
                    student.user.delete()
                    deleted_count += 1
                except Student.DoesNotExist:
                    messages.error(request, f"Student with ID {student_id} not found.")
                except Exception as e:
                    messages.error(request, f"Error deleting student: {str(e)}")
            
            messages.success(request, f"Successfully deleted {deleted_count} selected 5th year students.")
            return redirect('admin_students')
    
    # Get year level counts for context
    year_counts = Student.objects.values('year_level').annotate(count=Count('id')).order_by('year_level')
    year_count_dict = {item['year_level']: item['count'] for item in year_counts}
    
    return render(request, 'admin/remove_fifth_year_students.html', {
        'fifth_year_students': fifth_year_students,
        'count': count,
        'year_counts': year_count_dict,
    })
