# Hospital Patient Records Management System (H-PRMS)

A comprehensive hospital management system built with Python Flask backend and React frontend for managing patient records, appointments, and medical data.

## 🏥 Features

- **Patient Management**: Complete patient registration, medical history, and document management
- **Appointment Scheduling**: Efficient appointment booking and management system
- **Medical Records**: Secure storage and retrieval of medical records and lab results
- **User Management**: Role-based access control for different hospital staff
- **Reports & Analytics**: Comprehensive reporting and data visualization
- **Security**: JWT authentication, role-based permissions, and data encryption

## 🏗️ Architecture

### Backend (Python Flask)
- **Framework**: Flask with Flask-JWT-Extended
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT tokens with refresh mechanism
- **API**: RESTful API with standardized responses

### Frontend (React)
- **Framework**: React 18 with React Router
- **Styling**: TailwindCSS with custom components
- **State Management**: React Context API
- **HTTP Client**: Axios with interceptors

### Database Schema
- **Patients**: Personal info, medical history, allergies, medications
- **Users**: Authentication, roles, permissions
- **Appointments**: Scheduling, status tracking
- **Medical Records**: Diagnosis, treatment, vital signs
- **Lab Tests**: Results, attachments, status

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB 5.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Hospital-Patient-Records-Management-System
   ```

2. **Set up Python Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Set up Environment Variables**
   ```bash
   # Backend
   cp .env.example .env
   # Edit .env with your configuration
   
   # Frontend
   cd frontend
   cp .env.example .env
   # Edit .env with your configuration
   cd ..
   ```

6. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running on localhost:27017
   mongod
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   python backend/app.py
   ```
   The API will be available at `http://localhost:5000`

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm start
   ```
   The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
Hospital-Patient-Records-Management-System/
├── backend/                    # Python Flask backend
│   ├── app.py                 # Main Flask application
│   ├── config/                # Configuration files
│   ├── controllers/           # Request handlers
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   ├── middleware/            # Custom middleware
│   └── utils/                 # Utility functions
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── context/           # React Context providers
│   │   ├── services/          # API services
│   │   ├── hooks/             # Custom hooks
│   │   └── utils/             # Utility functions
│   └── public/                # Static files
├── docs/                      # Documentation
├── shared/                    # Shared resources
└── venv/                      # Python virtual environment
```

## 🔐 Authentication & Authorization

### User Roles
- **Admin**: Full system access
- **Doctor**: Medical records and appointments
- **Nurse**: Patient care and vital signs
- **Receptionist**: Patient registration and appointments
- **Patient**: Own records and appointments

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile

#### Patients
- `GET /api/patients` - Get all patients
- `POST /api/patients` - Create new patient
- `GET /api/patients/:id` - Get patient details
- `PUT /api/patients/:id` - Update patient
- `DELETE /api/patients/:id` - Delete patient

#### Appointments
- `GET /api/appointments` - Get appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/:id` - Update appointment
- `DELETE /api/appointments/:id` - Cancel appointment

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Documentation

The API follows RESTful conventions with standardized response formats:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "statusCode": 200,
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "statusCode": 400,
  "error": {
    "code": "ERROR_CODE",
    "details": [ ... ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
- `MONGODB_URI`: MongoDB connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `DEBUG`: Enable debug mode

#### Frontend (.env)
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_NAME`: Application name

## 🚀 Deployment

### Backend Deployment
1. Set production environment variables
2. Install production dependencies
3. Use Gunicorn as WSGI server
4. Configure reverse proxy (Nginx)

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to static hosting service
3. Configure API URL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- Basic patient management
- User authentication
- Appointment scheduling
- Medical records

---

**Built with ❤️ for healthcare professionals**
