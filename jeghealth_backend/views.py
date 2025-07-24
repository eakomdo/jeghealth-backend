from django.http import HttpResponse
from django.conf import settings


def welcome_view(request):
    """
    Welcome page for JEGHealth Backend API
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JEGHealth Backend API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 800px;
                width: 90%;
                text-align: center;
            }
            h1 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 40px;
                font-size: 1.2em;
            }
            .links-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .link-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                padding: 25px;
                border-radius: 15px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                display: block;
            }
            .link-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
                text-decoration: none;
                color: white;
            }
            .link-title {
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .link-description {
                font-size: 0.9em;
                opacity: 0.9;
            }
            .features {
                margin-top: 40px;
                text-align: left;
            }
            .features h3 {
                color: #667eea;
                margin-bottom: 15px;
                text-align: center;
            }
            .features ul {
                list-style: none;
                padding: 0;
            }
            .features li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .features li::before {
                content: "✅ ";
                margin-right: 10px;
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 30px;
                border: 1px solid #c3e6cb;
            }
            .admin-creds {
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                border: 1px solid #ffeaa7;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 JEGHealth Backend API</h1>
            <p class="subtitle">Secure, Scalable Healthcare Data Management System</p>
            
            <div class="status">
                <strong>🟢 Server Status:</strong> Running and Ready for Testing!
            </div>

            <div class="links-grid">
                <a href="/api/docs/" class="link-card">
                    <div class="link-title">📚 Swagger UI</div>
                    <div class="link-description">Interactive API testing and documentation</div>
                </a>
                
                <a href="/api/redoc/" class="link-card">
                    <div class="link-title">📖 ReDoc</div>
                    <div class="link-description">Beautiful API documentation</div>
                </a>
                
                <a href="/admin/" class="link-card">
                    <div class="link-title">⚙️ Admin Panel</div>
                    <div class="link-description">Database management interface</div>
                </a>
                
                <a href="/api/v1/auth/" class="link-card">
                    <div class="link-title">🔐 Auth API</div>
                    <div class="link-description">User authentication endpoints</div>
                </a>
            </div>

            <div class="admin-creds">
                <strong>🔑 Admin Credentials:</strong><br>
                <strong>Username:</strong> admin<br>
                <strong>Password:</strong> adminpassword123
            </div>

            <div class="features">
                <h3>🚀 Available Features</h3>
                <ul>
                    <li><strong>User Management:</strong> Registration, authentication, profiles, and role-based permissions</li>
                    <li><strong>Health Metrics:</strong> Blood pressure, heart rate, weight, sleep tracking, and analytics</li>
                    <li><strong>IoT Integration:</strong> Device registration, bulk data uploads, and real-time alerts</li>
                    <li><strong>Appointments:</strong> Scheduling, management, and notifications</li>
                    <li><strong>Medications:</strong> Tracking, reminders, and dosage management</li>
                    <li><strong>Security:</strong> JWT authentication, CORS support, and data validation</li>
                    <li><strong>API Documentation:</strong> Comprehensive Swagger/OpenAPI docs</li>
                    <li><strong>Admin Interface:</strong> Full database management capabilities</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)
