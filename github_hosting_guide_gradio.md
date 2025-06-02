# GitHub Hosting Guide for Gradio E-Invoice Chatbot

This guide provides step-by-step instructions for hosting your Gradio-based e-invoice chatbot on GitHub and deploying it using Hugging Face Spaces.

## 1. Prepare Your Repository

### 1.1 Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "e-invoice-chatbot")
4. Add a description (optional)
5. Choose public or private visibility
6. Initialize with a README file
7. Click "Create repository"

### 1.2 Organize Your Project Files

Ensure your project has the following structure:
```
e-invoice-chatbot/
├── app.py                  # Renamed from app_gradio.py
├── data_router.py
├── response_handler.py
├── response_generator.py
├── visualization_generator.py
├── requirements.txt        # Renamed from requirements_gradio.txt
├── README.md
└── output/                 # Directory for data files
    ├── invoices.csv
    ├── items.csv
    ├── taxpayers.csv
    └── invoice_audit_logs.csv
```

### 1.3 Update README.md

Create a comprehensive README.md file with:
- Project description
- Features
- Installation instructions
- Usage guide
- Screenshots (optional)
- License information

## 2. Push Your Code to GitHub

### 2.1 Clone the Repository Locally

```bash
git clone https://github.com/yourusername/e-invoice-chatbot.git
cd e-invoice-chatbot
```

### 2.2 Add Your Files

```bash
# Copy your project files to the repository directory
cp -r /path/to/your/chatbot/* .

# Rename app_gradio.py to app.py
mv app_gradio.py app.py

# Rename requirements_gradio.txt to requirements.txt
mv requirements_gradio.txt requirements.txt
```

### 2.3 Commit and Push

```bash
git add .
git commit -m "Initial commit of e-invoice chatbot with Gradio UI"
git push origin main
```

## 3. Deploy on Hugging Face Spaces

Hugging Face Spaces provides free hosting for Gradio applications with direct GitHub integration.

### 3.1 Create a Hugging Face Account

1. Go to [Hugging Face](https://huggingface.co/) and sign up for an account
2. Verify your email address

### 3.2 Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - Owner: Your username
   - Space name: e-invoice-chatbot (or your preferred name)
   - License: Choose appropriate license
   - SDK: Gradio
   - Space hardware: CPU (free tier)
   - Visibility: Public or Private

### 3.3 Connect to GitHub Repository

1. In your new Space, go to the "Files" tab
2. Click on "Manage repository access"
3. Select "Link to GitHub repository"
4. Authorize Hugging Face to access your GitHub account
5. Select your e-invoice-chatbot repository
6. Choose the branch (usually "main")
7. Click "Save"

### 3.4 Configure the Space

1. Create a file named `.gitattributes` in your repository with the following content:
```
*.csv filter=lfs diff=lfs merge=lfs -text
```

2. If your data files are large, consider using Git LFS:
```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
git commit -m "Configure Git LFS for data files"
git push origin main
```

3. Create a file named `requirements.txt` in your repository (if not already done) with all dependencies

### 3.5 Deploy Your App

1. Hugging Face will automatically deploy your app when you push changes to GitHub
2. Monitor the build logs for any errors
3. Once deployed, your app will be available at `https://huggingface.co/spaces/yourusername/e-invoice-chatbot`

## 4. Alternative Deployment Options

### 4.1 Gradio Share (Temporary Demos)

For quick, temporary demos (up to 72 hours):

```python
# At the end of your app.py file
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)  # Adds share=True parameter
```

This will generate a public URL that remains active for up to 72 hours.

### 4.2 Self-Hosting with Flask

For more permanent self-hosting:

1. Create a `wsgi.py` file:
```python
from app import create_interface

demo = create_interface()
app = demo.app

if __name__ == "__main__":
    app.run()
```

2. Deploy using Gunicorn:
```bash
pip install gunicorn
gunicorn wsgi:app
```

### 4.3 Docker Deployment

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

2. Build and run the Docker container:
```bash
docker build -t e-invoice-chatbot .
docker run -p 7860:7860 e-invoice-chatbot
```

## 5. Managing the OpenAI API Key

For security reasons, never commit your API key to GitHub. Instead:

### 5.1 Using Environment Variables

1. Create a `.env` file locally (add to .gitignore):
```
OPENAI_API_KEY=your_api_key_here
```

2. Update your app to use the environment variable:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### 5.2 Using Hugging Face Secrets

1. In your Hugging Face Space, go to the "Settings" tab
2. Click on "Repository secrets"
3. Add a new secret with key "OPENAI_API_KEY" and your API key as the value
4. Update your app to use this secret:
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

## 6. Troubleshooting Common Issues

### 6.1 Dependencies Issues

If you encounter dependency issues during deployment:
- Ensure all dependencies are listed in `requirements.txt`
- Specify exact versions to avoid compatibility issues
- Consider using a `runtime.txt` file to specify the Python version

### 6.2 File Path Issues

If your app can't find data files:
- Use relative paths from the application root
- Ensure data files are included in your repository
- Check file permissions

### 6.3 Memory or Performance Issues

If your app is slow or crashes:
- Optimize data loading with caching
- Reduce the size of data files
- Consider upgrading to a paid tier with more resources

## 7. Updating Your Deployment

To update your deployed app:
1. Make changes to your local code
2. Commit and push to GitHub
3. Hugging Face will automatically redeploy your app

## 8. Custom Domain (Optional)

For a professional touch, you can set up a custom domain:
1. In your Hugging Face Space settings, go to "Custom domain"
2. Follow the instructions to configure DNS settings for your domain
3. Wait for DNS propagation (can take up to 48 hours)

## 9. Monitoring and Analytics

To monitor usage of your chatbot:
1. In your Hugging Face Space, go to the "Analytics" tab
2. View metrics like visitors, requests, and errors
3. Consider implementing custom logging for more detailed analytics
