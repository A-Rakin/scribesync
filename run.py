from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting ScribeSync...")

    # Show current working directory
    print(f"Current directory: {os.getcwd()}")

    # Check templates folder
    templates_path = os.path.join(os.getcwd(), 'templates')
    print(f"Templates path: {templates_path}")
    print(f"Templates exists: {os.path.exists(templates_path)}")

    if os.path.exists(templates_path):
        print("\nFiles in templates folder:")
        for file in os.listdir(templates_path):
            print(f"  - {file}")

    # Check Flask's template folder
    print(f"\nFlask template_folder: {app.template_folder}")
    print(f"Flask root_path: {app.root_path}")

    # Create database tables
    with app.app_context():
        db.create_all()
        print("\n✅ Database initialized")

    print("\n🌐 Server starting on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)