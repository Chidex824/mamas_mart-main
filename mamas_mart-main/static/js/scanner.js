/**
 * Mamas Mart - QR / Barcode Scanner
 * Uses the html5-qrcode library (loaded via CDN in the template).
 *
 * Public API (called from page-specific inline scripts):
 *   MamasScanner.open(options)
 *
 * options = {
 *   onSuccess: function(decodedText, decodedResult) { ... },
 *   title:     String  (optional modal title)
 * }
 */

const MamasScanner = (() => {
  let html5QrCode = null;
  const SCANNER_ELEMENT_ID = 'mamas-qr-reader';
  const MODAL_ID           = 'mamasScannerModal';

  /** Build the modal once and append it to <body> */
  function ensureModal() {
    if (document.getElementById(MODAL_ID)) return;

    const html = `
      <div class="modal fade" id="${MODAL_ID}" tabindex="-1" aria-labelledby="${MODAL_ID}Label" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" style="max-width:480px">
          <div class="modal-content rounded-4 shadow-lg border-0">
            <div class="modal-header" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff">
              <h5 class="modal-title fw-bold d-flex align-items-center gap-2" id="${MODAL_ID}Label">
                <i class="ti ti-scan fs-4"></i>
                <span id="mamas-scanner-title">Scan QR / Barcode</span>
              </h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-3">
              <p class="text-muted small mb-2 text-center">
                <i class="ti ti-info-circle me-1"></i>
                Point camera at a QR code or barcode
              </p>
              <!-- Scanner viewport -->
              <div id="${SCANNER_ELEMENT_ID}" style="width:100%;border-radius:12px;overflow:hidden;"></div>
              <!-- Status message -->
              <div id="mamas-scanner-status" class="mt-3 text-center small text-muted"></div>
              <!-- Manual input fallback -->
              <div class="mt-3 border-top pt-3">
                <label class="form-label small fw-semibold">Or enter code manually:</label>
                <div class="input-group">
                  <input type="text" id="mamas-manual-code" class="form-control form-control-sm"
                         placeholder="Type barcode / QR value…" autocomplete="off">
                  <button class="btn btn-outline-primary btn-sm" id="mamas-manual-submit" type="button">
                    <i class="ti ti-arrow-right"></i> Use
                  </button>
                </div>
              </div>
            </div>
            <div class="modal-footer border-0 pt-0">
              <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">
                <i class="ti ti-x me-1"></i>Close
              </button>
            </div>
          </div>
        </div>
      </div>`;

    document.body.insertAdjacentHTML('beforeend', html);
  }

  function setStatus(msg, cls = 'text-muted') {
    const el = document.getElementById('mamas-scanner-status');
    if (el) {
      el.className = `mt-3 text-center small ${cls}`;
      el.textContent = msg;
    }
  }

  /** Stop the camera and clean up */
  function stopScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
      html5QrCode.stop().catch(() => {});
    }
    // clear the reader div so it can be re-initialised next time
    const el = document.getElementById(SCANNER_ELEMENT_ID);
    if (el) el.innerHTML = '';
  }

  /**
   * Open the scanner modal.
   * @param {object} options - { onSuccess, title }
   */
  function open(options = {}) {
    ensureModal();

    const { onSuccess, title = 'Scan QR / Barcode' } = options;

    // Set modal title
    const titleEl = document.getElementById('mamas-scanner-title');
    if (titleEl) titleEl.textContent = title;

    // Show the Bootstrap modal
    const modalEl  = document.getElementById(MODAL_ID);
    const bsModal  = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();

    setStatus('Starting camera…');

    // Start camera after modal is fully shown (so the viewport has size)
    modalEl.addEventListener('shown.bs.modal', function startOnShow() {
      modalEl.removeEventListener('shown.bs.modal', startOnShow);
      startCamera(onSuccess, bsModal);
    }, { once: true });

    // Stop camera when modal closes
    modalEl.addEventListener('hide.bs.modal', function stopOnHide() {
      modalEl.removeEventListener('hide.bs.modal', stopOnHide);
      stopScanner();
    }, { once: true });

    // Manual entry button
    const manualBtn = document.getElementById('mamas-manual-submit');
    const manualInput = document.getElementById('mamas-manual-code');
    if (manualBtn && manualInput) {
      // Clone to remove old listeners
      const newBtn = manualBtn.cloneNode(true);
      manualBtn.parentNode.replaceChild(newBtn, manualBtn);
      document.getElementById('mamas-manual-submit').addEventListener('click', () => {
        const code = (document.getElementById('mamas-manual-code').value || '').trim();
        if (!code) return;
        stopScanner();
        bsModal.hide();
        if (typeof onSuccess === 'function') onSuccess(code, null);
      });
    }
  }

  function startCamera(onSuccess, bsModal) {
    html5QrCode = new Html5Qrcode(SCANNER_ELEMENT_ID);

    const config = {
      fps: 12,
      qrbox: { width: 260, height: 180 },
      aspectRatio: 1.5,
      supportedScanTypes: [
        Html5QrcodeScanType.SCAN_TYPE_CAMERA
      ]
    };

    html5QrCode.start(
      { facingMode: 'environment' },   // rear camera
      config,
      (decodedText, decodedResult) => {
        // Success — stop camera, close modal, call callback
        stopScanner();
        setStatus(`✓ Scanned: ${decodedText}`, 'text-success fw-semibold');
        bsModal.hide();
        if (typeof onSuccess === 'function') {
          onSuccess(decodedText, decodedResult);
        }
      },
      () => { /* ignore per-frame errors */ }
    ).then(() => {
      setStatus('Camera active — point at a code', 'text-success');
    }).catch(err => {
      console.error('Scanner error:', err);
      setStatus('⚠ Camera not available. Use manual entry below.', 'text-warning');
    });
  }

  return { open };
})();
