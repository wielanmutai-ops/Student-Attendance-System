import os

templates = {
    'templates/attendance/manage_levels.html': '''{% extends 'base.html' %}
{% block title %}Manage Levels{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-layer-group"></i> Manage Levels</h2>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <p>Manage academic levels here.</p>
            <a href="{% url 'create_level' %}" class="btn btn-primary">Add Level</a>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/create_level.html': '''{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Create Level{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-layer-group"></i> Create Academic Level</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <button type="submit" class="btn btn-primary">Create Level</button>
                        <a href="{% url 'manage_levels' %}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/manage_courses.html': '''{% extends 'base.html' %}
{% block title %}Manage Courses{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-graduation-cap"></i> Manage Courses</h2>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <p>Manage academic courses here.</p>
            <a href="{% url 'create_course' %}" class="btn btn-primary">Add Course</a>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/create_course.html': '''{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Create Course{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0"><i class="fas fa-graduation-cap"></i> Create Course</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <button type="submit" class="btn btn-success">Create Course</button>
                        <a href="{% url 'manage_courses' %}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/manage_units.html': '''{% extends 'base.html' %}
{% block title %}Manage Units{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-book"></i> Manage Units</h2>
        </div>
    </div>
    <div class="card">
        <div class="card-body">
            <p>Manage academic units here.</p>
            <a href="{% url 'create_unit' %}" class="btn btn-primary">Add Unit</a>
            <a href="{% url 'assign_units' %}" class="btn btn-warning">Assign Units</a>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/create_unit.html': '''{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Create Unit{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0"><i class="fas fa-book"></i> Create Unit</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <button type="submit" class="btn btn-info">Create Unit</button>
                        <a href="{% url 'manage_units' %}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
    
    'templates/attendance/assign_units.html': '''{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Assign Units{% endblock %}
{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-warning text-white">
                    <h4 class="mb-0"><i class="fas fa-user-tie"></i> Assign Units to Lecturer</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <button type="submit" class="btn btn-warning">Assign Units</button>
                        <a href="{% url 'manage_units' %}" class="btn btn-secondary">Cancel</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
}

# Create template files
os.makedirs('templates/attendance', exist_ok=True)

for filename, content in templates.items():
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filename}")
    else:
        print(f"Exists: {filename}")