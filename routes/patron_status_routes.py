from flask import Blueprint, render_template, request, flash
from services.library_service import get_patron_status_report

patron_status_bp = Blueprint('patrons', __name__)

@patron_status_bp.route('/patron_status', methods=['GET', 'POST'])
def patron_status():
    """
    Implements R7: Patron Status
    """
    report = None
    if request.method == 'POST':
        patron_id = request.form.get('patron_id', '').strip()
        report = get_patron_status_report(patron_id)
        if not report['success']:
            flash(report['message'], 'error')
            report = None
    return render_template('patron_status.html', report=report)
