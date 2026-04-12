import io
from io import BytesIO
import uuid
import json
import qrcode
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import white, black, orange, lightgrey

from PIL import Image as PILImage

from .models import Booking, PromoCode
from apps.events.models import Ticket


@login_required
def booking_create(request, ticket_id):
    """
    View for selecting ticket quantity and creating a pending booking.
    Redirects to checkout after successful creation.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid quantity (at least 1).")
            return render(request, 'bookings/booking_form.html', {
                'ticket': ticket,
                'event': event,
            })

        if quantity > ticket.tickets_remaining:
            messages.error(request, f"Only {ticket.tickets_remaining} tickets remaining.")
            return render(request, 'bookings/booking_form.html', {
                'ticket': ticket,
                'event': event,
            })

        booking = Booking.objects.create(
            user=request.user,
            ticket=ticket,
            quantity=quantity,
            total_price=ticket.price * quantity,
            status='PENDING'
        )

        messages.success(request, "Booking created successfully! Proceed to payment.")
        return redirect('bookings:checkout', booking_id=booking.id)

    return render(request, 'bookings/booking_form.html', {
        'ticket': ticket,
        'event': event,
    })


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'PENDING':
        messages.error(request, "This booking cannot be paid anymore.")
        return redirect('events:event_detail', pk=booking.ticket.event.pk)

    promo_code = None
    discount_amount = Decimal('0.00')
    final_total = booking.total_price

    if request.method == 'POST':
        # Check if this is a promo code submission
        if 'promo_code' in request.POST:
            promo_input = request.POST.get('promo_code', '').strip().upper()

            if promo_input:
                try:
                    promo = PromoCode.objects.get(
                        code=promo_input,
                        is_active=True,
                        event=booking.ticket.event
                    )

                    if promo.expires_at and promo.expires_at < timezone.now():
                        messages.error(request, "This promo code has expired.")
                    elif promo.used_count >= promo.max_uses:
                        messages.error(request, "This promo code has reached its usage limit.")
                    else:
                        discount_rate = Decimal(promo.discount_percent) / Decimal('100')
                        discount_amount = booking.total_price * discount_rate
                        final_total = booking.total_price - discount_amount

                        promo.used_count += 1
                        promo.save()

                        messages.success(request, f"Promo code {promo.code} applied! {promo.discount_percent}% off")
                        promo_code = promo

                except PromoCode.DoesNotExist:
                    messages.error(request, "Invalid promo code for this event.")

            # After promo is applied, stay on the same page (no redirect to payment yet)
            # We will handle payment in a separate POST

        # If this is the final payment submission (phone number submitted)
        elif 'phone' in request.POST:
            # TODO: Here you will call Buni with final_total
            messages.info(request, f"Payment initiated for KES {final_total} with Buni...")
            # For now just redirect to detail with success
            return redirect('bookings:booking_detail', booking_id=booking.id)

    context = {
        'booking': booking,
        'ticket': booking.ticket,
        'event': booking.ticket.event,
        'promo_code': promo_code,
        'discount_amount': discount_amount,
        'final_total': final_total,
    }

    return render(request, 'bookings/checkout.html', context)


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    context = {
        'booking': booking,
        'ticket': booking.ticket,
        'event': booking.ticket.event,
    }

    return render(request, 'bookings/booking_detail.html', context)


@login_required
def download_tickets(request, booking_id):
    """
    Generate PDF tickets with:
    - Front: event poster background + ticket type + attendee name
    - Back: event details + UNIQUE QR code (new every download)
    - QR code raised higher to avoid overlapping footer
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if not booking.is_paid:
        messages.error(request, "Tickets can only be downloaded after payment.")
        return redirect('bookings:booking_detail', booking_id=booking.id)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(85*mm, 55*mm))

    attendee_data = booking.attendee_names

    if isinstance(attendee_data, str):
        try:
            attendee_data = json.loads(attendee_data)
        except json.JSONDecodeError:
            attendee_data = []

    if booking.quantity == 1 or not attendee_data:
        user = booking.user
        if hasattr(user, 'first_name') and hasattr(user, 'last_name'):
            buyer_name = f"{user.first_name} {user.last_name}".strip()
        else:
            email_prefix = user.email.split('@')[0]
            buyer_name = email_prefix.replace('.', ' ').replace('_', ' ').title()
        names = [buyer_name or "Attendee"]
    else:
        names = attendee_data[:booking.quantity]

    for idx, attendee in enumerate(names):
        pdf.setPageSize((85*mm, 55*mm))

        if booking.ticket.event.image:
            try:
                img_path = booking.ticket.event.image.path
                img = PILImage.open(img_path)
                scale = max(85*mm / img.width, 55*mm / img.height)
                w = img.width * scale
                h = img.height * scale
                x = (85*mm - w) / 2
                y = (55*mm - h) / 2
                pdf.drawInlineImage(img_path, x, y, width=w, height=h)
            except:
                pdf.setFillColor(black)
                pdf.rect(0, 0, 85*mm, 55*mm, fill=1)

        pdf.setFillColorRGB(0, 0, 0, 0.65)
        pdf.rect(0, 0, 85*mm, 55*mm, fill=1)

        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(42.5*mm, 32*mm, booking.ticket.name.upper())

        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawCentredString(42.5*mm, 18*mm, attendee.upper()[:25])

        pdf.showPage()

        pdf.setPageSize((85*mm, 55*mm))

        pdf.setFillColorRGB(10/255, 10/255, 35/255)
        pdf.rect(0, 0, 85*mm, 55*mm, fill=1)

        pdf.setStrokeColorRGB(1, 0.5, 0)
        pdf.setLineWidth(1.5)
        pdf.rect(4*mm, 4*mm, 77*mm, 47*mm)

        pdf.setFillColor(orange)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawCentredString(42.5*mm, 48*mm, "EVENT DETAILS")

        pdf.setFillColor(white)
        pdf.setFont("Helvetica", 8)
        y = 42*mm
        lines = [
            f"Location: {booking.ticket.event.location[:38]}",
            f"Date: {booking.ticket.event.event_date.strftime('%d %b %Y')}",
            f"Time: {booking.ticket.event.event_time.strftime('%I:%M %p')}",
            f"Type: {booking.ticket.name}",
        ]
        for line in lines:
            pdf.drawString(8*mm, y, line)
            y -= 7*mm

        pdf.setFont("Helvetica-Oblique", 7)
        pdf.setFillColor(lightgrey)
        pdf.drawCentredString(42.5*mm, 8*mm, "Ticket2X.com developed by Wesa Mwiti")

        random_token = str(uuid.uuid4())[:8]
        qr_data = f"https://{request.get_host()}/events/{booking.ticket.event.id}/?ticket={booking.id}-{idx+1}-{random_token}"

        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_pil = PILImage.open(qr_buffer)

        pdf.drawInlineImage(qr_pil, 58*mm, 16*mm, width=22*mm, height=22*mm)

        pdf.setFont("Helvetica", 6)
        pdf.setFillColor(lightgrey)
        pdf.drawCentredString(69*mm, 12*mm, "Scan to View Event")

        if idx < len(names) - 1:
            pdf.showPage()

    pdf.save()
    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket2x_booking_{booking.id}.pdf"'
    response.write(pdf_content)
    return response


@staff_member_required
def qr_scanner(request):
    return render(request, 'bookings/admin_qr_scanner.html')

@staff_member_required
@csrf_exempt
def validate_qr(request):
    if request.method != 'POST':
        return JsonResponse({'valid': False, 'message': 'Invalid request method'})

    try:
        # Improved body reading
        body = request.body.decode('utf-8')
        if not body:
            raise ValueError("Empty request body")

        data = json.loads(body)
        qr_data = data.get('qr_data', '').strip()
        action = data.get('action')

        if not qr_data:
            raise ValueError("No qr_data received")

        if '?ticket=' not in qr_data:
            raise ValueError("Invalid QR format - missing ?ticket=")

        # Parse the QR data
        ticket_part = qr_data.split('?ticket=')[1]
        booking_id_str, idx_str, token = ticket_part.split('-')
        booking_id = int(booking_id_str)
        ticket_index = int(idx_str)

        booking = get_object_or_404(Booking, id=booking_id)

        # === Your existing logic here (latest token + scanned check) ===
        if booking.scanned:
            return JsonResponse({
                'valid': False,
                'message': f'Ticket already used on {booking.scanned_at.strftime("%d %b %Y at %H:%M")}'
            })

        if booking.latest_qr_token != token:
            return JsonResponse({
                'valid': False,
                'message': 'This QR code is outdated. Please download the ticket again.'
            })

        # Valid scan
        if not action:
            return JsonResponse({
                'valid': True,
                'booking_id': booking.id,
                'ticket_index': ticket_index,
                'message': f'VALID TICKET #{ticket_index} • {booking.ticket.event.title}'
            })

        # Approve
        if action == 'approve':
            booking.scanned = True
            booking.scanned_at = timezone.now()
            booking.status = 'USED'
            booking.save()
            return JsonResponse({
                'success': True,
                'message': f'✓ Entry Approved! Ticket #{ticket_index} marked as USED.'
            })

        return JsonResponse({'success': True, 'message': 'Action recorded'})

    except json.JSONDecodeError:
        return JsonResponse({'valid': False, 'message': 'Invalid JSON format from scanner'})
    except ValueError as e:
        return JsonResponse({'valid': False, 'message': str(e)})
    except Exception as e:
        # Log the real error so you can see it in Render logs
        print("QR Scanner Error:", str(e))   # ← Check your server logs for this line
        return JsonResponse({'valid': False, 'message': 'Error processing QR code'})

# ──────────────────────────────────────────────
# NEW: Admin view to generate random 6-digit promo code for a specific event
# ──────────────────────────────────────────────
@staff_member_required
def generate_promo_code(request, event_id):
    """
    Generate a random 6-digit numeric promo code for a specific event.
    Admin can call this from event change page or promo list.
    """
    if request.method == 'POST':
        # Generate random 6-digit code
        code = ''.join(random.choices('0123456789', k=6))  # e.g. "483921"

        # Ensure uniqueness
        while PromoCode.objects.filter(code=code).exists():
            code = ''.join(random.choices('0123456789', k=6))

        # Create promo tied to this event
        promo = PromoCode.objects.create(
            code=code,
            discount_percent=10,  # default – edit in admin
            event_id=event_id,
            max_uses=50,          # default – edit in admin
            description=f"Generated for event {event_id}",
            is_active=True
        )

        messages.success(request, f"New promo code generated: **{code}** (10% off – edit in admin)")
        return redirect('admin:bookings_promocode_changelist')  # go to promo list

    return redirect('admin:bookings_promocode_changelist')

@login_required
def my_tickets(request):
    """Show user's tickets: Pending, Paid, and Downloaded"""
    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/my_tickets.html', context)

# ====================== NEW PAYMENT VIEWS ======================

@login_required
def card_payment(request, booking_id):
    """Placeholder for Card Payment (Buni integration coming on Monday)"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
        'final_total': booking.total_price,
    }
    return render(request, 'bookings/card_payment.html', context)


@login_required
def bank_payment(request, booking_id):
    """Placeholder for Bank Transfer Payment (Buni integration coming on Monday)"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
        'final_total': booking.total_price,
    }
    return render(request, 'bookings/bank_payment.html', context)