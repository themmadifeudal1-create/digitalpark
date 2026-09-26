import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "app", "static", "ParkIQ_Hackathon_Pitch_and_Technical_Guide.pdf")

def create_hackathon_pdf(output_path=PDF_OUTPUT_PATH):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Theme Palette
    c_primary = colors.HexColor("#0f172a")     # Deep Slate
    c_accent = colors.HexColor("#0284c7")      # Cyan/Blue Accent
    c_emerald = colors.HexColor("#059669")     # Green
    c_amber = colors.HexColor("#d97706")       # Amber
    c_dark = colors.HexColor("#1e293b")        # Dark slate
    c_light = colors.HexColor("#f8fafc")       # Off-white

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_accent,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    quote_style = ParagraphStyle(
        'PitchQuote',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title Banner
    story.append(Paragraph("ParkIQ — Smart Campus Parking Platform", title_style))
    story.append(Paragraph("HACKATHON PRESENTATION & TECHNICAL DEFENSE GUIDE (S.M.A.R.T. EDITION 2026)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=2, spaceAfter=10))

    # Section 1: The 30-Second Elevator Pitch
    story.append(Paragraph("1. The 30-Second Hook & Elevator Pitch", h1_style))
    pitch_text = (
        "\"Good morning, Judges. Most teams build parking systems as simple CRUD apps with static QR images. "
        "If the internet fails, they crash. If two users click at once, they double-book. And they only tell you what is happening right now.<br/><br/>"
        "We built <b>ParkIQ</b> around the <b>S.M.A.R.T. model</b>: it doesn't just book parking — <b>it predicts it</b>. "
        "With a sub-second Realtime Digital Twin, timetable-aware class booking, cryptographic single-use QR passes that verify offline at the gate, "
        "and 48-hour AI occupancy forecasting, ParkIQ turns campus parking into an intelligent, self-balancing ecosystem.\""
    )
    story.append(Paragraph(pitch_text, quote_style))

    # Section 2: The 2-Minute Live Demo Flow
    story.append(Spacer(1, 4))
    story.append(Paragraph("2. The 2-Minute Live Demo Flow (Step-by-Step on Screen)", h1_style))
    story.append(Paragraph("Run this exact sequence on your live app at <b>http://127.0.0.1:8000</b>:", body_style))

    demo_data = [
        [Paragraph("Time", table_header_style), Paragraph("Screen / Tab", table_header_style), Paragraph("Action on Screen", table_header_style), Paragraph("What to Say to Judges", table_header_style)],
        [
            Paragraph("<b>0:00 - 0:30</b>", table_cell_style),
            Paragraph("Digital Twin Map", table_cell_style),
            Paragraph("Click slot, drag Replay Scrubber slider", table_cell_style),
            Paragraph("\"Every physical slot is a live state cell pushed over WebSockets in &lt;1s. Admins can scrub back in time to analyze peak flows.\"", table_cell_style)
        ],
        [
            Paragraph("<b>0:30 - 0:50</b>", table_cell_style),
            Paragraph("AI Forecast & GreenMeter", table_cell_style),
            Paragraph("Point to 48h heatmap & alert note", table_cell_style),
            Paragraph("\"Our Prophet model predicts occupancy for the next 48 hours: 'P1 full by 9:40, P3 has space till 11:15' — preventing bottlenecks before arrival.\"", table_cell_style)
        ],
        [
            Paragraph("<b>0:50 - 1:10</b>", table_cell_style),
            Paragraph("ClassSync & Booking", table_cell_style),
            Paragraph("Click '1-Tap ClassSync Auto-Book'", table_cell_style),
            Paragraph("\"ClassSync reads student timetable, detects 10:00 AM class in Block C, picks nearest Lot P1 (85m walk) + 15 min buffer.\"", table_cell_style)
        ],
        [
            Paragraph("<b>1:10 - 1:20</b>", table_cell_style),
            Paragraph("My Passes & QR", table_cell_style),
            Paragraph("Show generated ticket & HMAC badge", table_cell_style),
            Paragraph("\"Pass issued with signed HMAC-SHA256 token. Not a guessable database ID — mathematically tamper-proof.\"", table_cell_style)
        ],
        [
            Paragraph("<b>1:20 - 1:35</b>", table_cell_style),
            Paragraph("EdgeGuard Kiosk", table_cell_style),
            Paragraph("Click Check-In; barrier arm swings 90 deg", table_cell_style),
            Paragraph("\"Kiosk verifies signature and lifts barrier. In the background, the slot flips red across all browsers in real time.\"", table_cell_style)
        ],
        [
            Paragraph("<b>1:35 - 1:45</b>", table_cell_style),
            Paragraph("Attack Demo (Viva Gold!)", table_cell_style),
            Paragraph("Click 'Attack: Tampered QR'", table_cell_style),
            Paragraph("\"Forged signatures or yesterday's screenshots are rejected locally at the edge before even touching the database.\"", table_cell_style)
        ],
        [
            Paragraph("<b>1:45 - 2:00</b>", table_cell_style),
            Paragraph("Check-Out & GreenMeter", table_cell_style),
            Paragraph("Click 'Check-Out' or 'Leaving Campus'", table_cell_style),
            Paragraph("\"Geofence closes session, frees slot to green, and logs savings: 14 search-mins avoided & 0.63 kg CO2 prevented.\"", table_cell_style)
        ]
    ]

    t_demo = Table(demo_data, colWidths=[55, 95, 140, 240])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_demo)

    # Page Break for Technical Methods
    story.append(PageBreak())

    # Section 3: Technical Methods & Formulations
    story.append(Paragraph("3. Technical Methods & Algorithms Used", h1_style))
    story.append(Paragraph("Structure your explanation around these 6 core engineering methods:", body_style))

    # A. Concurrency & DB Overlap Constraint
    story.append(Paragraph("A. Concurrency & Double-Booking Prevention (Database Engine Level)", h2_style))
    story.append(Paragraph("<b>Method:</b> Atomic Database Constraint Triggers + Transactional Row Locking.", bullet_style))
    story.append(Paragraph(
        "<b>Implementation:</b> Instead of fragile application-level checks, SQLite/PostgreSQL triggers "
        "execute on <code>BEFORE INSERT / UPDATE</code> on the <code>reservations</code> entity. "
        "The trigger raises an <code>ABORT</code> exception if <code>EXISTS (SELECT 1 WHERE slot_id = NEW.slot_id AND NOT (end_time &lt;= NEW.start_time OR start_time &gt;= NEW.end_time))</code>. "
        "Any overlapping concurrent request is rejected with a <code>409 Conflict</code>.",
        body_style
    ))

    # B. Cryptographic Ticket Verification & EdgeGuard
    story.append(Paragraph("B. Cryptographic Ticket Verification & EdgeGuard Offline Kiosks", h2_style))
    story.append(Paragraph("<b>Method:</b> Symmetric HMAC-SHA256 Signed JSON Web Tokens (JWT) + Single-Use State Ledger.", bullet_style))
    story.append(Paragraph(
        "<b>Payload Structure:</b> <code>Payload = { reservationId, userId, slotId, exp }</code><br/>"
        "<b>Signature:</b> <code>HMAC-SHA256(Payload, SERVER_SECRET)</code><br/>"
        "<b>Offline Resilience:</b> Kiosks verify signatures locally using cached secrets even if campus WiFi disconnects. "
        "Single-use replay protection is verified against the <code>qr_tokens.used_at</code> timestamp.",
        body_style
    ))

    # C. Machine Learning 48-Hour Occupancy Forecasting
    story.append(Paragraph("C. Machine Learning 48-Hour Occupancy Forecasting (Prophet/LSTM Model)", h2_style))
    story.append(Paragraph("<b>Method:</b> Additive Time-Series Decomposition parameterized by time-of-day, weekday, and campus calendar.", bullet_style))
    story.append(Paragraph(
        "<b>Formula:</b> <code>Y_hat(t, lot) = BaseHourCurve(t) * LotDemandMultiplier * WeekdayFactor + EventModifier</code><br/>"
        "Generates hourly occupancy projections and actionable alerts ('P1 will be full by 9:40 — P3 has space till 11:15').",
        body_style
    ))

    # D. ClassSync Heuristic Allocation
    story.append(Paragraph("D. ClassSync Heuristic Allocation (Timetable Integration)", h2_style))
    story.append(Paragraph("<b>Method:</b> Distance Matrix Optimization + Schedule Window Buffer.", bullet_style))
    story.append(Paragraph(
        "<b>Optimization:</b> <code>SelectedLot = argmin_{lot in FreeLots} Distance(ClassBlock, Lot)</code><br/>"
        "Automatically configures the booking window: <code>[ClassStart - 10 min, ClassEnd + 15 min buffer]</code>.",
        body_style
    ))

    # E. Geofencing Boundary Detection & GreenMeter
    story.append(Paragraph("E. Geofencing Boundary Detection (Haversine Formula) & Sustainability", h2_style))
    story.append(Paragraph("<b>Method:</b> Great-circle distance computation between driver GPS and the 300m campus boundary.", bullet_style))
    story.append(Paragraph(
        "<b>Haversine Distance:</b> <code>d = 2R * arcsin(sqrt(sin^2(dLat/2) + cos(lat1)*cos(lat2)*sin^2(dLon/2)))</code><br/>"
        "Departing vehicles past 300m trigger a 5-minute grace period before auto-checkout.<br/>"
        "<b>GreenMeter:</b> <code>CO2_Avoided (kg) = Sessions * 14 search-mins * 0.045 kg/min</code>",
        body_style
    ))

    # Section 4: Us vs. Other Teams
    story.append(Spacer(1, 4))
    story.append(Paragraph("4. Us vs. Other Teams (The Competitive Moat)", h1_style))

    moat_data = [
        [Paragraph("Dimension", table_header_style), Paragraph("Typical Hackathon Project", table_header_style), Paragraph("ParkIQ (Your Project)", table_header_style)],
        [Paragraph("<b>Availability</b>", table_cell_style), Paragraph("Manual browser page refresh", table_cell_style), Paragraph("WebSocket push &lt;1s + 48-hour AI forecast heatmap", table_cell_style)],
        [Paragraph("<b>Slot Choice</b>", table_cell_style), Paragraph("User manually guesses slots", table_cell_style), Paragraph("ClassSync suggests nearest lot to next class + duration buffer", table_cell_style)],
        [Paragraph("<b>Gate Security</b>", table_cell_style), Paragraph("Raw booking ID in QR (forgeable)", table_cell_style), Paragraph("HMAC-SHA256 signed single-use JWT with edge kiosk check", table_cell_style)],
        [Paragraph("<b>WiFi Outage</b>", table_cell_style), Paragraph("Cloud-only (dies offline)", table_cell_style), Paragraph("EdgeGuard Kiosk verifies locally and queues cloud sync", table_cell_style)],
        [Paragraph("<b>Check-Out</b>", table_cell_style), Paragraph("Manual button click only", table_cell_style), Paragraph("Scan or Geofence auto check-out upon leaving campus", table_cell_style)],
        [Paragraph("<b>No-Shows</b>", table_cell_style), Paragraph("Slot stays blocked forever", table_cell_style), Paragraph("20-minute background auto-expiry worker frees slot", table_cell_style)],
        [Paragraph("<b>Data Story</b>", table_cell_style), Paragraph("Static CRUD database tables", table_cell_style), Paragraph("Digital Twin map + GreenMeter CO2 + FairFlow rewards", table_cell_style)]
    ]

    t_moat = Table(moat_data, colWidths=[90, 180, 260])
    t_moat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_moat)

    # Page Break for Viva Q&A
    story.append(PageBreak())

    # Section 5: The 8 Tough Questions Judges Will Ask
    story.append(Paragraph("5. The 8 Questions Judges Will Actually Ask & Your Answers", h1_style))

    qas = [
        (
            "Q1. How do you prevent two users booking the same slot at the exact same millisecond?",
            "A: Database-level atomicity, not front-end code. We use transactional row locks (SELECT ... FOR UPDATE) and an atomic database trigger (prevent_reservation_overlap) that evaluates range collisions. If two simultaneous requests arrive, the database engine aborts the second with a 409 Conflict."
        ),
        (
            "Q2. Why a signed JWT inside the QR code instead of just a booking ID?",
            "A: A raw ID is easily guessable and forgeable. An HMAC-SHA256 signature mathematically proves server origin; the 'exp' claim stops screenshot reuse; and the qr_tokens ledger on the backend enforces single-use replay protection."
        ),
        (
            "Q3. What happens if the campus WiFi is down at the entry gate?",
            "A: EdgeGuard kiosks verify the HMAC signature locally using cached secrets without cloud access. Valid drivers enter without interruption; check-in events are queued locally and synchronized to the cloud once connectivity resumes."
        ),
        (
            "Q4. How does Geofence auto check-out work?",
            "A: The PWA computes haversine distance to the 300m campus boundary. When the vehicle exits, a 5-minute departure grace period activates. If departure is sustained, the session auto-closes, the slot is freed, and a sustainability receipt is generated."
        ),
        (
            "Q5. What happens when a user reserves a slot and never shows up?",
            "A: An automated background worker runs every 30 seconds. If 20 minutes elapse past the scheduled start time without a gate check-in, the reservation auto-expires, the slot returns to AVAILABLE, and the user is alerted."
        ),
        (
            "Q6. Where does the training data for your AI forecasting come from?",
            "A: The model initializes on historical and synthetic session logs parameterized by hour-of-day, weekday curves, and campus events. As live trips occur, the data self-improves to capture real seasonal habits."
        ),
        (
            "Q7. Why not Automatic Number Plate Recognition (ANPR) cameras everywhere instead of QR?",
            "A: Cost and privacy. High-speed ANPR cameras are expensive across multiple gates. QR is zero-cost and universal. However, ParkIQ implements Triple-ID: QR is primary, ANPR is an optional express lane for faculty, and RFID cards serve as fallback."
        ),
        (
            "Q8. How would you scale this to 5 or 10 campus locations?",
            "A: The API is stateless behind a reverse proxy. Campuses and lots are partitioned rows in the database, not separate codebases. An MQTT broker fans out per-slot sensor telemetry, and read-replicas serve high-volume availability queries."
        )
    ]

    for q, a in qas:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))
        story.append(Spacer(1, 2))

    # Section 6: Winning Closing Line
    story.append(Spacer(1, 6))
    story.append(Paragraph("6. The Winning Closing Line", h1_style))
    closing_text = (
        "\"Judges, we didn't just digitize campus parking — <b>we predicted it</b>. "
        "ParkIQ turns every parking slot on campus into a live, intelligent, self-managing resource. Thank you!\""
    )
    story.append(Paragraph(closing_text, quote_style))

    # Build PDF
    doc.build(story)
    print(f"[SUCCESS] PDF Generated at: {output_path}")

if __name__ == "__main__":
    create_hackathon_pdf()
