Kisan-Setu Final BCA Project

Includes:
- HTML templates
- CSS styling
- JavaScript validation/search/filter/calculation
- Python Flask backend
- Supabase/PostgreSQL integration using supabase-py
- Register/Login
- Farmer Dashboard
- Buyer Dashboard
- Add/Edit/Delete Product
- Browse/Search/Filter Products
- Place Order
- Dummy Payment
- Order Success
- Database Status Page
- Error handling with try-except
- Hosting-ready files

Run Locally:
1. pip install -r requirements.txt
2. Supabase -> SQL Editor -> run supabase_setup.sql
3. Rename .env.example to .env
4. Fill:
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-publishable-or-anon-key
5. python app.py
6. Open http://127.0.0.1:5000

Demo Logins after running SQL:
Farmer: farmer@test.com / 1234
Buyer: buyer@test.com / 1234

Render Hosting:
- Push to GitHub
- Render -> New Web Service
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app
- Add SUPABASE_URL and SUPABASE_KEY in Environment Variables
- Deploy
