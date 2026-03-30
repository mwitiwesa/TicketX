# TicketX - Event Ticketing Platform

**A modern, secure, and scalable event ticketing system built with Django.**

TicketX simplifies the entire event management process — from ticket creation and sales to on-ground validation. Designed for the African market, it combines beautiful user experience with powerful admin tools, including dynamic QR code scanning and flexible promo code management.

Whether you're organizing concerts, sports events, corporate functions, or cultural festivals, TicketX gives you full control and delivers a seamless experience to your attendees.

---

## ✨ Key Features

### For Attendees
- Browse and discover events with an intuitive interface
- Easy ticket booking with quantity selection and attendee name collection
- **Promo Code System** – Apply event-specific discount codes at checkout
- Secure checkout flow with real-time discount calculation
- Instant download of beautifully designed PDF tickets with event branding
- Unique, reload-proof QR codes on every ticket (prevents screenshot reuse)

### For Admins & Organizers
- Complete admin dashboard to manage events, tickets, and bookings
- **Live QR Code Scanner** – Use your phone or tablet to validate tickets at the gate
- **Advanced Promo Code Management** – Create event-specific codes with percentage discounts
- **Random 6-Digit Code Generation** – Instantly generate secure promo codes
- Usage tracking and limits per promo code
- Detailed booking and validation history
- Support for multiple ticket types per event (Regular, VIP, Early Bird, etc.)

### Technical Excellence
- Fully responsive and modern UI
- Secure authentication and authorization
- Event-specific promo codes (prevents cross-event misuse)
- Dynamic QR code generation (changes on every download)
- Safe decimal calculations for discounts
- Production-ready structure with proper static/media file handling

---

## 🛠 Tech Stack

- **Backend**: Django 6.0
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Payment Gateway**: Buni (M-Pesa integration ready)
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode + Pillow
- **Deployment**: Render, Railway, Vercel, or any Python hosting platform

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd TicketX

Create and activate a virtual environmentBashpython -m venv env
source env/bin/activate        # On Windows: env\Scripts\activate
Install dependenciesBashpip install -r requirements.txt
Apply database migrationsBashpython manage.py makemigrations
python manage.py migrate
Create a superuserBashpython manage.py createsuperuser
Run the development serverBashpython manage.py runserver
Access the platform
Main site: http://127.0.0.1:8000
Admin panel: http://127.0.0.1:8000/admin/



📋 Features Overview
Event Management

Create and manage events with rich details, dates, locations, and posters
Support for multiple ticket types per event
Real-time ticket availability tracking

Booking & Payment Flow

Flexible quantity selection with attendee name input
Promo code application with instant discount preview
Secure checkout experience
Ready for Buni Payment Gateway integration

Ticket Experience

Professional PDF tickets featuring event poster and attendee names
Unique, dynamic QR codes (regenerates on every download to prevent reuse)
Easy download and sharing options

Admin & Operations

Live QR scanner for fast and accurate gate entry validation
Comprehensive booking and user management
Promo code creation with event targeting and usage limits
Random 6-digit promo code generator for influencers and promoters
Full tracking of promo usage and ticket validation history


🎯 Target Users

Event Organizers – Concerts, sports tournaments, festivals, and conferences
Corporate Teams – Team building, product launches, and private events
Influencers & Promoters – Exclusive promo codes for their followers
Attendees – Anyone seeking a smooth and reliable ticketing experience


🔮 Future Roadmap

Full Buni Payment Gateway integration (M-Pesa, Cards, Bank transfers)
Email and SMS ticket delivery
Advanced analytics and reporting dashboard
Mobile application (React Native)
Refund and cancellation management
Waitlist and sold-out handling
Multi-language support


📄 License
This project is licensed under the MIT License.

🤝 Contributing
Contributions, issues, and feature requests are welcome!

Fork the project
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request


📞 Support & Contact
Developer: Wesa Mwiti
Email: mwitiwesa@gmail.com

Built with ❤️ for the African event industry