/**
 * Kristu Jayanti University - Smart Campus Venue & Facility Management Engine
 * File: web/static/app.js
 * 
 * Interactive Client Controller connecting the modern UI to pure Data Structure APIs:
 * - Augmented AVL Interval Tree (clash detection, timeline rendering)
 * - Custom Singly Linked List (venue registry & pointer chain)
 * - Custom Binary Search Tree (venue indexing & 3-case deletion)
 * - Custom Linked Stack (undo recovery)
 * - Custom Linked Queue (FIFO waitlist counter)
 * - Custom Binary Max-Heap (priority allocation engine)
 * - Stack-based expression evaluation for facility setup scores
 * - Adjacency List Graph + Min-Heap Dijkstra (campus venue wayfinding)
 */

let currentPortal = localStorage.getItem("kju_portal") || "user";
let allVenues = [];
let selectedVenueId = "ske_auditorium";
let currentRouteNodeIds = new Set();
let campusLandmarks = [];
let campusPathways = [];

// INITIALIZATION
// ----------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    applyPortalState();
    initNavigationTabs();
    initForms();
    loadVenues();
    loadWaitlist();
    loadPriorityRequests();
    loadCampusMap();
    loadLiveBenchmarks();
    loadPendingBookings();
    loadUserRequests();
});

function initNavigationTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            switchNavTab(tabId);
        });
    });
}

function switchNavTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

    const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const targetPanel = document.getElementById(tabId);

    if (targetBtn) targetBtn.classList.add("active");
    if (targetPanel) targetPanel.classList.add("active");

    if (tabId === "tabBookings") {
        loadBookings(selectedVenueId);
        loadPendingBookings();
        loadUserRequests();
        refreshIntervalTreeAscii();
    } else if (tabId === "tabNavigation") {
        setTimeout(renderSvgMap, 50);
    }
}

function switchPortal(portal) {
    currentPortal = portal;
    localStorage.setItem("kju_portal", portal);
    applyPortalState();
}

function applyPortalState() {
    document.body.setAttribute("data-portal", currentPortal);

    const btnUser = document.getElementById("btnUserPortal");
    const btnAdmin = document.getElementById("btnAdminPortal");
    const roleInd = document.getElementById("portalRoleIndicator");
    const formHeading = document.getElementById("bookingFormHeading");
    const formBadge = document.getElementById("bookingFormBadge");
    const formDesc = document.getElementById("bookingFormDescription");
    const submitBtn = document.getElementById("bookSubmitBtn");

    if (currentPortal === "admin") {
        if (btnAdmin) {
            btnAdmin.classList.add("admin-active");
            btnAdmin.classList.remove("active");
        }
        if (btnUser) btnUser.classList.remove("active");
        if (roleInd) roleInd.textContent = "Admin Portal";
        if (formHeading) formHeading.textContent = "Admin Direct Schedule";
        if (formBadge) {
            formBadge.textContent = "Direct Schedule";
            formBadge.className = "badge badge-rose";
        }
        if (formDesc) formDesc.textContent = "Admin Mode: Direct slot scheduling into the AVL Interval Tree with automated conflict detection.";
        if (submitBtn) submitBtn.innerHTML = "⚡ Confirm Direct Schedule";
        loadPendingBookings();
    } else {
        if (btnUser) btnUser.classList.add("active");
        if (btnAdmin) btnAdmin.classList.remove("admin-active", "active");
        if (roleInd) roleInd.textContent = "User Portal";
        if (formHeading) formHeading.textContent = "Request Venue Booking";
        if (formBadge) {
            formBadge.textContent = "User Portal";
            formBadge.className = "badge badge-emerald";
        }
        if (formDesc) formDesc.textContent = "Select auditorium or lab, event interval, and submit. Your request is queued for Admin approval.";
        if (submitBtn) submitBtn.innerHTML = "📩 Submit Booking Request";
        loadUserRequests();
    }
}

function initForms() {
    // Venue Form
    const vForm = document.getElementById("venueForm");
    if (vForm) {
        vForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                venue_id: document.getElementById("vidInput").value.trim(),
                name: document.getElementById("vnameInput").value.trim(),
                building: document.getElementById("vbuildingInput").value.trim(),
                category: document.getElementById("vcategoryInput").value,
                capacity: parseInt(document.getElementById("vcapacityInput").value, 10),
                usage_policy: document.getElementById("vpolicyInput") ? document.getElementById("vpolicyInput").value.trim() : "College Academic Use",
                at_front: document.getElementById("vAtFront") ? document.getElementById("vAtFront").checked : false
            };

            fetch("/api/venues", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    vForm.reset();
                    loadVenues();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(err => console.error(err));
        });
    }

    // Booking Form
    const bForm = document.getElementById("bookingForm");
    if (bForm) {
        const bookingDateInput = document.getElementById("bookDate");
        if (bookingDateInput) {
            bookingDateInput.addEventListener("change", () => {
                loadBookings(selectedVenueId, bookingDateInput.value);
            });
        }

        bForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const clashAlert = document.getElementById("clashAlertBox");
            if (clashAlert) clashAlert.style.display = "none";

            const payload = {
                venue_id: document.getElementById("bookVenueSelect").value,
                title: document.getElementById("bookTitle").value.trim(),
                organizer: document.getElementById("bookOrganizer").value.trim(),
                start_time: document.getElementById("bookStartTime").value,
                end_time: document.getElementById("bookEndTime").value,
                date: document.getElementById("bookDate").value,
                role: currentPortal
            };

            const submitBtn = document.getElementById("bookSubmitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Submitting...";
            }

            fetch("/api/bookings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json().then(data => ({ status: res.status, data })))
            .then(({ status, data }) => {
                if (status === 202 && data.success) {
                    alert(`📩 Booking Request Submitted!\nYour request (${data.request_id || data.booking?.booking_id}) for "${payload.title}" has been sent to Campus Admin for approval.`);
                    bForm.reset();
                    document.getElementById("bookVenueSelect").value = payload.venue_id;
                    document.getElementById("bookDate").value = payload.date;
                    document.getElementById("bookStartTime").value = "14:00";
                    document.getElementById("bookEndTime").value = "16:00";
                    loadUserRequests();
                    loadPendingBookings();
                    loadBookings(payload.venue_id, payload.date);
                } else if (status === 201 && data.success) {
                    alert("✅ Slot Scheduled Successfully! Added to AVL Interval Tree.");
                    bForm.reset();
                    document.getElementById("bookVenueSelect").value = payload.venue_id;
                    document.getElementById("bookDate").value = payload.date;
                    document.getElementById("bookStartTime").value = "14:00";
                    document.getElementById("bookEndTime").value = "16:00";
                    loadBookings(payload.venue_id, payload.date);
                    loadPendingBookings();
                    loadUserRequests();
                    refreshIntervalTreeAscii();
                    updateTotalBookingsKpi();
                } else if (status === 409) {
                    if (clashAlert) {
                        clashAlert.style.display = "block";
                        const msgEl = document.getElementById("clashAlertMsg");
                        const clashList = data.clashes ? data.clashes.map(c => `• ${c.title} (${c.start_time_str} - ${c.end_time_str})`).join("<br>") : "";
                        msgEl.innerHTML = `<strong>${data.message}</strong><br><div style="margin-top:4px;">${clashList}</div>`;
                    }
                } else {
                    alert("Error: " + (data.message || "Failed to process booking request."));
                }
            })
            .catch(err => {
                console.error(err);
                alert("The booking request could not reach the server. Check that the Smart Campus app is running, then try again.");
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    applyPortalState();
                }
            });
        });
    }

    // Waitlist Form
    const wForm = document.getElementById("waitlistForm");
    if (wForm) {
        wForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                venue_id: document.getElementById("waitlistVenue").value,
                title: document.getElementById("waitlistTitle").value.trim(),
                organizer: document.getElementById("waitlistOrganizer").value.trim(),
                time_slot: document.getElementById("waitlistTimeSlot").value.trim()
            };

            fetch("/api/waitlist", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("🎫 " + data.message);
                    wForm.reset();
                    loadWaitlist();
                } else {
                    alert("Error: " + data.message);
                }
            });
        });
    }

    // Priority Form
    const pForm = document.getElementById("priorityForm");
    if (pForm) {
        pForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById("prioTitle").value.trim(),
                venue_id: document.getElementById("prioVenue").value,
                organizer: document.getElementById("prioOrganizer").value.trim(),
                priority_score: parseFloat(document.getElementById("prioScore").value)
            };

            fetch("/api/priority-requests", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("👑 " + data.message);
                    pForm.reset();
                    loadPriorityRequests();
                } else {
                    alert("Error: " + data.message);
                }
            });
        });
    }

}

// ----------------------------------------------------------------------------
// 1. VENUES & LINKED LIST CONTROLLER
// ----------------------------------------------------------------------------

function loadVenues() {
    fetch("/api/venues")
        .then(res => res.json())
        .then(data => {
            allVenues = data.venues || [];
            document.getElementById("dashVenueCount").innerText = allVenues.length;

            renderVenueTable(allVenues);
            renderPointerChain(data.pointer_chain || []);
            populateVenueDropdowns(allVenues);
            renderAnalyticsTable(allVenues);

            // Trigger booking load for default selected venue
            if (allVenues.length > 0) {
                if (!allVenues.find(v => v.id === selectedVenueId)) {
                    selectedVenueId = allVenues[0].id;
                }
                loadBookings(selectedVenueId);
            }
        })
        .catch(err => console.error(err));
}

function renderVenueTable(venues) {
    const tbody = document.getElementById("venueTableBody");
    if (!tbody) return;

    if (venues.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2rem; color: var(--text-muted);">No venues registered.</td></tr>`;
        return;
    }

    tbody.innerHTML = venues.map(v => `
        <tr>
            <td><code style="color:var(--accent-blue); font-weight:600;">${v.id}</code></td>
            <td><strong>${v.name}</strong></td>
            <td>${v.building}</td>
            <td><span class="badge badge-purple">${v.category}</span></td>
            <td><span class="badge badge-cyan">${v.capacity} seats</span></td>
            <td>${v.sound_system || 'Integrated Audio'}</td>
            <td><span style="font-size:0.75rem; color:var(--text-secondary);">${v.usage_policy || 'College Use Only'}</span></td>
            <td>
                <button class="btn btn-secondary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem; color: var(--accent-rose);" onclick="deleteVenue('${v.id}')">
                    Delete
                </button>
            </td>
        </tr>
    `).join("");
}

function renderPointerChain(chain) {
    const container = document.getElementById("venuePointerChain");
    if (!container) return;

    if (chain.length === 0) {
        container.innerHTML = `<span style="color:var(--text-muted); font-size: 0.8rem;">[ Head: NULL ]</span>`;
        return;
    }

    const items = chain.map((node, idx) => `
        <div style="display:inline-flex; align-items:center; margin-bottom: 0.4rem;">
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--border-accent); border-radius: 6px; padding: 0.4rem 0.6rem; font-size: 0.75rem; text-align: left;">
                <span style="color:var(--accent-blue); font-weight:700;">${idx === 0 ? 'HEAD: ' : ''}${node.venue_id}</span>
                <span style="color:var(--text-muted); font-size: 0.7rem; display:block;">Cap: ${node.capacity}</span>
            </div>
            <span style="color:var(--accent-indigo); font-size: 0.9rem; margin: 0 0.35rem;">➔</span>
        </div>
    `).join("");

    container.innerHTML = items + `<div style="display:inline-flex; align-items:center;"><span style="color:var(--text-muted); font-size: 0.75rem; background: rgba(0,0,0,0.4); padding: 0.3rem 0.5rem; border-radius:4px;">NULL</span></div>`;
}

function populateVenueDropdowns(venues) {
    const selects = ["bookVenueSelect", "waitlistVenue", "prioVenue"];
    selects.forEach(selId => {
        const el = document.getElementById(selId);
        if (!el) return;
        const curVal = el.value;
        el.innerHTML = venues.map(v => `<option value="${v.id}">${v.name} (${v.capacity} seats)</option>`).join("");
        if (curVal && venues.find(v => v.id === curVal)) {
            el.value = curVal;
        }
    });

    const navStart = document.getElementById("navStartSelect");
    if (navStart) {
        navStart.innerHTML = `
            <option value="main_gate">Gate 1</option>
            <option value="gate_2">Gate 2 (Vehicular)</option>
            <option value="main_block">Main Block</option>
            <option value="cs_block">PG Block</option>
            <option value="admin_block">Admin Block</option>
            <option value="humanities_block">Humanities Block</option>
            <option value="admin_parking">Admin Block Basement Parking</option>
            <option value="humanities_parking">Humanities Block Basement Parking</option>
        `;
    }

    const navDest = document.getElementById("navDestSelect");
    if (navDest) {
        navDest.innerHTML = `
            <option value="admin_parking">Admin Block Basement Parking</option>
            <option value="humanities_parking">Humanities Block Basement Parking</option>
            <option value="main_block">Main Block</option>
            <option value="cs_block">PG Block</option>
            <option value="admin_block">Admin Block</option>
            <option value="humanities_block">Humanities Block</option>
            <option value="main_gate">Gate 1</option>
            <option value="gate_2">Gate 2</option>
        `;
    }
}

function filterVenueTable() {
    const query = (document.getElementById("venueSearchInput").value || "").toLowerCase();
    const cat = document.getElementById("venueCategoryFilter").value;

    const filtered = allVenues.filter(v => {
        const matchesQuery = v.name.toLowerCase().includes(query) || v.id.toLowerCase().includes(query) || v.building.toLowerCase().includes(query);
        const matchesCat = cat === "ALL" || v.category === cat;
        return matchesQuery && matchesCat;
    });

    renderVenueTable(filtered);
}

function deleteVenue(vid) {
    if (!confirm(`Are you sure you want to delete venue '${vid}' from Linked List & BST?`)) return;

    fetch(`/api/venues/${vid}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            loadVenues();
        });
}

function reverseVenueList() {
    fetch("/api/venues/reverse", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert("🔄 " + data.message);
            loadVenues();
        });
}

function undoVenueAction() {
    fetch("/api/venues/undo", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            alert("↩️ " + data.message);
            loadVenues();
        });
}

function loadBstTraversals(type) {
    fetch("/api/venues/bst-traversals")
        .then(res => res.json())
        .then(data => {
            const box = document.getElementById("bstOutputBox");
            const nodes = data[type] || [];
            if (nodes.length === 0) {
                box.innerText = `BST is empty.`;
                return;
            }
            box.innerText = `${type.toUpperCase()} TRAVERSAL (${nodes.length} nodes, Height: ${data.height}):\n` +
                nodes.map((n, idx) => `[${idx + 1}] Key: ${n.key} ➔ Venue: ${n.value.name} (Cap: ${n.value.capacity})`).join("\n");
        });
}

// ----------------------------------------------------------------------------
// 2. VENUE BOOKINGS & INTERVAL TIMELINE CONTROLLER
// ----------------------------------------------------------------------------

function onBookingVenueChanged() {
    const sel = document.getElementById("bookVenueSelect");
    if (!sel) return;
    selectedVenueId = sel.value;
    loadBookings(selectedVenueId, document.getElementById("bookDate")?.value);
    refreshIntervalTreeAscii();
}

function loadBookings(venueId, date = document.getElementById("bookDate")?.value) {
    selectedVenueId = venueId;
    const v = allVenues.find(item => item.id === venueId);
    const titleEl = document.getElementById("timelineVenueTitle");
    const badgeEl = document.getElementById("timelineVenueBadge");

    if (titleEl) titleEl.innerText = v ? `Schedule: ${v.name}` : `Venue Schedule: ${venueId}`;
    if (badgeEl) badgeEl.innerText = venueId;

    const query = new URLSearchParams({ venue_id: venueId });
    if (date) query.set("date", date);
    fetch(`/api/bookings?${query.toString()}`)
        .then(res => res.json())
        .then(bookings => {
            renderTimelineTrack(bookings);
            renderBookingsTable(bookings);
            updateTotalBookingsKpi();
        })
        .catch(err => console.error(err));
}

function updateTotalBookingsKpi() {
    fetch("/api/bookings")
        .then(res => res.json())
        .then(allB => {
            const kpi = document.getElementById("dashBookingCount");
            if (kpi) kpi.innerText = allB.length;
        });
}

function renderTimelineTrack(bookings) {
    const track = document.getElementById("timelineTrack");
    if (!track) return;

    // Timeline spans 08:00 (480 min) to 20:00 (1200 min) -> Total 720 minutes
    const dayStart = 480;
    const totalDayMins = 720;

    track.innerHTML = "";

    bookings.forEach(b => {
        const leftPercent = Math.max(0, Math.min(100, ((b.start_min - dayStart) / totalDayMins) * 100));
        const widthPercent = Math.max(2, Math.min(100 - leftPercent, ((b.end_min - b.start_min) / totalDayMins) * 100));

        const block = document.createElement("div");
        block.className = "timeline-event-block";
        block.style.left = `${leftPercent}%`;
        block.style.width = `${widthPercent}%`;
        block.title = `${b.title} (${b.start_time_str} - ${b.end_time_str})`;

        block.innerHTML = `
            <div style="font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${b.title}</div>
            <div style="font-size:0.68rem; opacity:0.85;">${b.start_time_str} - ${b.end_time_str}</div>
        `;

        track.appendChild(block);
    });
}

function renderBookingsTable(bookings) {
    const tbody = document.getElementById("bookingsTableBody");
    if (!tbody) return;

    if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 1.5rem; color: var(--text-muted);">No reservations booked for this venue. Hall is 100% available.</td></tr>`;
        return;
    }

    tbody.innerHTML = bookings.map(b => {
        const durHours = ((b.end_min - b.start_min) / 60).toFixed(1);
        return `
            <tr>
                <td><code style="color:var(--accent-blue); font-weight:600;">${b.booking_id}</code></td>
                <td><strong>${b.title}</strong></td>
                <td>${b.organizer}</td>
                <td><span class="badge badge-emerald">${b.start_time_str} — ${b.end_time_str}</span></td>
                <td>${durHours} hrs</td>
                <td>
                    <button class="btn btn-secondary admin-only" style="padding: 0.25rem 0.6rem; font-size: 0.75rem; color: var(--accent-rose);" onclick="cancelBooking('${b.booking_id}')">
                        Cancel Slot
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function cancelBooking(bid) {
    if (!confirm(`Cancel reservation '${bid}' and remove from Interval Tree?`)) return;

    fetch(`/api/bookings/${bid}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            loadBookings(selectedVenueId);
            refreshIntervalTreeAscii();
        });
}

// ----------------------------------------------------------------------------
// ADMIN & USER BOOKING APPROVAL WORKFLOW
// ----------------------------------------------------------------------------

function loadPendingBookings() {
    fetch("/api/bookings/pending")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("adminPendingContainer");
            const badge = document.getElementById("adminPendingBadge");
            const countBadge = document.getElementById("adminPendingCountBadge");
            const pendingRequests = Array.isArray(data)
                ? data
                : (data.pending_requests || []);
            const count = pendingRequests.length;

            if (badge) {
                badge.innerText = count;
                badge.style.display = count > 0 ? "inline-block" : "none";
            }
            if (countBadge) {
                countBadge.innerText = `${count} Pending`;
            }

            if (!container) return;

            if (pendingRequests.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-muted); background: rgba(0,0,0,0.25); border-radius: 8px;">
                        <span style="font-size: 1.8rem; display:block; margin-bottom: 0.4rem;">🎉</span>
                        <strong>No Pending Booking Requests</strong>
                        <p style="font-size: 0.8rem; margin-top: 0.2rem;">All venue booking requests have been reviewed.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem;">
                    ${pendingRequests.map(req => {
                        const requestId = req.request_id || req.booking_id;
                        return `
                        <div style="background: rgba(19, 27, 46, 0.95); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; gap: 0.75rem;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
                                    <span class="badge badge-pending" style="font-size: 0.72rem;">⏳ ${requestId}</span>
                                    <span class="badge badge-cyan" style="font-size: 0.72rem;">${req.venue_id}</span>
                                </div>
                                <h4 style="font-size: 0.96rem; color: #fff; margin-bottom: 0.25rem;">${req.title}</h4>
                                <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                                    <strong>Dept:</strong> ${req.organizer}
                                </p>
                                <div style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--accent-emerald); background: rgba(0,0,0,0.3); padding: 0.35rem 0.5rem; border-radius: 6px;">
                                    📅 ${req.date} | ⏰ ${req.start_time_str} - ${req.end_time_str}
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.75rem;">
                                <button class="btn btn-primary" style="flex: 1; padding: 0.45rem 0.6rem; font-size: 0.8rem; background: linear-gradient(135deg, #10b981, #059669);" onclick="approveBookingRequest('${requestId}')">
                                    ✅ Approve
                                </button>
                                <button class="btn btn-secondary" style="flex: 1; padding: 0.45rem 0.6rem; font-size: 0.8rem; color: var(--accent-rose); border-color: rgba(244,63,94,0.4);" onclick="rejectBookingRequest('${requestId}')">
                                    ❌ Reject
                                </button>
                            </div>
                        </div>
                    `;
                    }).join("")}
                </div>
            `;
        })
        .catch(err => console.error("Error loading pending bookings:", err));
}

function approveBookingRequest(reqId) {
    fetch(`/api/bookings/${reqId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(({ status, data }) => {
        if (data.success) {
            alert(`✅ Approved!\nRequest ${reqId} has been approved and scheduled into the Interval Tree.`);
            loadPendingBookings();
            loadUserRequests();
            loadBookings(selectedVenueId);
            refreshIntervalTreeAscii();
            updateTotalBookingsKpi();
        } else {
            alert("Error: " + (data.message || "Failed to approve request."));
        }
    })
    .catch(err => console.error(err));
}

function rejectBookingRequest(reqId) {
    const reason = prompt("Enter rejection reason for request " + reqId + " (optional):", "Venue allocated for prior college convocation") || "Rejected by administration";
    fetch(`/api/bookings/${reqId}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: reason })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`❌ Rejected!\nRequest ${reqId} has been marked as rejected.`);
            loadPendingBookings();
            loadUserRequests();
        } else {
            alert("Error: " + (data.message || "Failed to reject request."));
        }
    })
    .catch(err => console.error(err));
}

function loadUserRequests() {
    fetch("/api/bookings/requests")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("userRequestsTableBody");
            if (!tbody) return;

            const reqs = Array.isArray(data) ? data : (data.requests || []);
            if (reqs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 1.5rem; color: var(--text-muted);">No booking requests submitted yet. Use the form below to request a venue slot.</td></tr>`;
                return;
            }

            tbody.innerHTML = reqs.map(r => {
                const requestId = r.request_id || r.booking_id;
                let badgeClass = "badge-pending";
                let badgeText = "⏳ Pending Approval";
                if (r.status === "Approved") {
                    badgeClass = "badge-approved";
                    badgeText = "✅ Approved";
                } else if (r.status === "Rejected") {
                    badgeClass = "badge-rejected";
                    badgeText = "❌ Rejected";
                }

                return `
                    <tr>
                        <td><code style="color:var(--accent-blue); font-weight:600;">${requestId}</code></td>
                        <td><strong>${r.title}</strong></td>
                        <td>${r.organizer}</td>
                        <td><span class="badge badge-cyan">${r.venue_id}</span></td>
                        <td><span style="font-family:var(--font-mono); font-size:0.78rem;">${r.date} (${r.start_time_str} - ${r.end_time_str})</span></td>
                        <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                        <td style="font-size:0.78rem; color:var(--text-secondary);">${r.rejection_reason || (r.status === "Approved" ? "Confirmed on Schedule" : "Under review by admin")}</td>
                    </tr>
                `;
            }).join("");
        })
        .catch(err => console.error("Error loading user requests:", err));
}

function refreshIntervalTreeAscii() {
    const box = document.getElementById("intervalTreeAscii");
    if (!box) return;

    fetch(`/api/venues/${selectedVenueId}/tree`)
        .then(res => res.json())
        .then(data => {
            box.innerText = data.tree_ascii || "Interval Tree is empty.";
        });
}

// ----------------------------------------------------------------------------
// 3. WAITLIST QUEUE CONTROLLER
// ----------------------------------------------------------------------------

function loadWaitlist() {
    fetch("/api/waitlist")
        .then(res => res.json())
        .then(data => {
            const kpi = document.getElementById("dashWaitlistCount");
            if (kpi) kpi.innerText = data.count || 0;

            const container = document.getElementById("waitlistQueueContainer");
            if (!container) return;

            const list = data.waitlist || [];
            if (list.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding: 2rem; color:var(--text-muted); width: 100%;">Waitlist queue is empty. All venue requests are currently served.</div>`;
                return;
            }

            container.innerHTML = list.map((item, idx) => `
                <div style="background: rgba(19, 27, 46, 0.85); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; position: relative;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                        <span class="badge badge-cyan" style="font-size: 0.75rem; font-weight:700;">${item.token}</span>
                        <span style="font-size: 0.72rem; color: var(--accent-amber); font-weight: 600;">Queue Position #${idx + 1}</span>
                    </div>
                    <h4 style="font-size: 0.92rem; margin-bottom: 0.2rem;">${item.title}</h4>
                    <p style="font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 0.2rem;">Venue: <code>${item.venue_id}</code></p>
                    <p style="font-size: 0.78rem; color: var(--text-muted);">Organizer: ${item.organizer} • Slot: ${item.time_slot}</p>
                </div>
            `).join("");
        });
}

function serveNextWaitlist() {
    fetch("/api/waitlist/serve", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`✅ Dequeued and Approved Token: ${data.item.token}\nEvent: '${data.item.title}'`);
                loadWaitlist();
            } else {
                alert(data.message);
            }
        });
}

// ----------------------------------------------------------------------------
// 4. PRIORITY EVENT ALLOCATION CONTROLLER (MAX-HEAP)
// ----------------------------------------------------------------------------

function loadPriorityRequests() {
    fetch("/api/priority-requests")
        .then(res => res.json())
        .then(data => {
            const kpi = document.getElementById("dashPriorityCount");
            if (kpi) kpi.innerText = data.count || 0;

            const grid = document.getElementById("priorityCardsGrid");
            if (!grid) return;

            const list = data.requests || [];
            if (list.length === 0) {
                grid.innerHTML = `<div style="text-align:center; padding: 2rem; color:var(--text-muted); width: 100%;">No pending priority event allocations.</div>`;
                return;
            }

            grid.innerHTML = list.map(item => `
                <div style="background: rgba(19, 27, 46, 0.85); border: 1px solid var(--border-accent); border-radius: 8px; padding: 1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                        <span class="badge badge-purple" style="font-weight:700;">Priority Score: ${item.priority_score.toFixed(1)}</span>
                        <code style="font-size: 0.75rem; color: var(--text-muted);">${item.request_id}</code>
                    </div>
                    <h4 style="font-size: 0.95rem; margin-bottom: 0.3rem;">${item.title}</h4>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">Target: <strong>${item.venue_id}</strong></p>
                    <p style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.6rem;">Authority: ${item.organizer}</p>
                    <div style="display:flex; gap: 0.4rem;">
                        <button class="btn btn-secondary" style="font-size: 0.72rem; padding: 0.2rem 0.5rem;" onclick="escalatePriorityPrompt('${item.request_id}', ${item.priority_score})">
                            ⚡ Escalate (+1.0)
                        </button>
                    </div>
                </div>
            `).join("");
        });
}

function dispatchTopPriority() {
    fetch("/api/priority-requests/dispatch", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(`🚀 Dispatched Highest Priority Event via Extract-Max:\n'${data.item.title}' (Score: ${data.item.priority_score})\nAssigned to ${data.item.venue_id}.`);
                loadPriorityRequests();
            } else {
                alert(data.message);
            }
        });
}

function escalatePriorityPrompt(reqId, curScore) {
    const newScore = Math.min(10.0, curScore + 1.0);
    fetch("/api/priority-requests/escalate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: reqId, new_priority: newScore })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            loadPriorityRequests();
        } else {
            alert(data.message);
        }
    });
}

// ----------------------------------------------------------------------------
// 5. ALGORITHMIC OPTIMIZERS
// ----------------------------------------------------------------------------

function runGreedyAlgorithm() {
    const container = document.getElementById("greedyResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Executing Greedy Activity Selection (Earliest Finish Time First)...</span>`;

    fetch("/api/algorithms/greedy-schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        const cards = data.selected_activities.map(a => `
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--accent-emerald); border-radius: 6px; padding: 0.8rem;">
                <span class="badge badge-emerald" style="font-size:0.7rem;">SELECTED SLOT</span>
                <h4 style="margin: 0.3rem 0; font-size: 0.9rem;">${a.name}</h4>
                <p style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--accent-cyan);">${a.start.toFixed(1)}:00 ➔ ${a.finish.toFixed(1)}:00</p>
            </div>
        `).join("");

        container.innerHTML = `
            <div style="margin-bottom: 0.8rem; font-size: 0.85rem; color: var(--accent-emerald);">
                ✓ Algorithm Selected <strong>${data.selected_count} Non-Overlapping Events</strong> Maximizing Hall Occupancy.
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem;">
                ${cards}
            </div>
        `;
    });
}

function runKnapsackAlgorithm() {
    const container = document.getElementById("knapsackResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Computing 0/1 Knapsack Dynamic Programming Table...</span>`;

    fetch("/api/algorithms/equipment-knapsack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ budget_or_power_limit: 110 })
    })
    .then(res => res.json())
    .then(data => {
        const items = data.selected_equipment.map(it => `
            <li style="margin-bottom: 0.3rem;">
                <strong>${it.name}</strong> — Cost / Load: ${it.cost} units | Utility: <span style="color:var(--accent-emerald); font-weight:700;">+${it.utility}</span>
            </li>
        `).join("");

        container.innerHTML = `
            <div style="background: rgba(11, 15, 25, 0.7); border: 1px solid var(--border-accent); border-radius: 8px; padding: 1rem;">
                <h3 style="color:var(--accent-blue); font-size: 1.1rem; margin-bottom: 0.4rem;">
                    Max Utility Achieved: <span style="color:var(--accent-emerald);">${data.max_utility} points</span> (Cap Limit: ${data.capacity_limit})
                </h3>
                <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.6rem;">Selected Optimal Equipment Combination:</p>
                <ul style="font-size: 0.82rem; padding-left: 1.25rem;">${items}</ul>
                <div style="margin-top: 0.6rem; font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">
                    DP Table Dimensions: ${data.dp_table_summary.rows} rows × ${data.dp_table_summary.cols} columns
                </div>
            </div>
        `;
    });
}

function runTimetableAlgorithm() {
    const container = document.getElementById("timetableResultContainer");
    container.innerHTML = `<span style="color:var(--accent-blue);">Solving Backtracking CSP with Pruning...</span>`;

    fetch("/api/algorithms/exam-timetable", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_venues: 3 })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.feasible) {
            container.innerHTML = `<span style="color:var(--accent-rose);">No clash-free assignment possible with current venue count.</span>`;
            return;
        }

        const entries = Object.entries(data.schedule).map(([course, venue]) => `
            <div style="background: rgba(19, 27, 46, 0.9); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.6rem 0.8rem;">
                <span style="font-size: 0.75rem; color: var(--text-muted); display:block;">Course</span>
                <strong style="color:#fff; font-size: 0.88rem;">${course}</strong>
                <div style="margin-top: 0.3rem; font-size: 0.78rem; color: var(--accent-emerald); font-weight:600;">➔ ${venue}</div>
            </div>
        `).join("");

        container.innerHTML = `
            <div style="margin-bottom: 0.8rem; font-size: 0.85rem; color: var(--accent-emerald);">
                ✓ Feasible Conflict-Free Schedule Found across <strong>${data.venues_used} Venues</strong> in ${data.backtrack_steps} recursive backtracking steps.
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem;">
                ${entries}
            </div>
        `;
    });
}

// ----------------------------------------------------------------------------
// 6. VENUE WAYFINDING & SVG MAP CONTROLLER (GRAPH + DIJKSTRA)
// ----------------------------------------------------------------------------

function loadCampusMap() {
    Promise.all([
        fetch("/api/landmarks").then(r => r.json()),
        fetch("/api/pathways").then(r => r.json())
    ]).then(([landmarks, pathways]) => {
        campusLandmarks = landmarks;
        campusPathways = pathways;
        renderSvgMap();
    });
}

function renderSvgMap() {
    const svg = document.getElementById("campusSvgMap");
    if (!svg || campusLandmarks.length === 0) return;

    svg.innerHTML = "";

    // Draw pathways
    campusPathways.forEach(pw => {
        const u = campusLandmarks.find(lm => lm.id === pw.source);
        const v = campusLandmarks.find(lm => lm.id === pw.dest);
        if (!u || !v) return;

        const isPartOfRoute = currentRouteNodeIds.has(pw.source) && currentRouteNodeIds.has(pw.dest);

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", u.x);
        line.setAttribute("y1", u.y);
        line.setAttribute("x2", v.x);
        line.setAttribute("y2", v.y);
        line.setAttribute("stroke", isPartOfRoute ? "var(--accent-emerald)" : "rgba(255,255,255,0.15)");
        line.setAttribute("stroke-width", isPartOfRoute ? "4" : "2");
        if (isPartOfRoute) {
            line.setAttribute("stroke-dasharray", "6,4");
        }
        svg.appendChild(line);
    });

    // Draw landmarks / venue nodes
    campusLandmarks.forEach(lm => {
        const isRoute = currentRouteNodeIds.has(lm.id);

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.style.cursor = "pointer";

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", lm.x);
        circle.setAttribute("cy", lm.y);
        circle.setAttribute("r", isRoute ? "14" : "10");
        circle.setAttribute("fill", isRoute ? "var(--accent-emerald)" : "var(--accent-blue)");
        circle.setAttribute("stroke", "#fff");
        circle.setAttribute("stroke-width", isRoute ? "3" : "2");

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", lm.x + 16);
        text.setAttribute("y", lm.y + 5);
        text.setAttribute("fill", isRoute ? "#34d399" : "#f1f5f9");
        text.setAttribute("font-size", isRoute ? "15px" : "14px");
        text.setAttribute("font-weight", "700");
        text.textContent = lm.name;

        g.appendChild(circle);
        g.appendChild(text);
        svg.appendChild(g);
    });
}

function findVenueRoute() {
    let startId = document.getElementById("navStartSelect").value;
    let destId = document.getElementById("navDestSelect").value;
    const accessibleOnly = document.getElementById("navWheelchair").checked;

    const venueToNode = {
        "jubilee_auditorium": "admin_block",
        "board_room_admin": "admin_block",
        "ske_auditorium": "cs_block",
        "cs_lab_ai": "cs_block",
        "m1_auditorium": "main_block",
        "m2_auditorium": "main_block",
        "m3_auditorium": "main_block",
        "m4_auditorium": "main_block",
        "cs_lab_turing": "main_block",
        "h1_auditorium": "humanities_block",
        "h2_auditorium": "humanities_block"
    };
    if (venueToNode[startId]) startId = venueToNode[startId];
    if (venueToNode[destId]) destId = venueToNode[destId];

    fetch("/api/navigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_id: startId, dest_id: destId, accessible_only: accessibleOnly })
    })
    .then(res => res.json())
    .then(data => {
        const resBox = document.getElementById("navRouteResult");
        if (!data.success || !data.route) {
            resBox.style.display = "block";
            document.getElementById("navDistanceText").innerText = "No route found under current constraints.";
            document.getElementById("navStepsContainer").innerHTML = "";
            currentRouteNodeIds.clear();
            renderSvgMap();
            return;
        }

        resBox.style.display = "block";
        const r = data.route;
        const dist = (r.total_distance_m !== undefined ? r.total_distance_m : (r.total_distance || 0)).toFixed(1);
        const estMin = r.estimated_minutes ? ` (~${r.estimated_minutes} min walk)` : "";
        document.getElementById("navDistanceText").innerHTML = `Total Walking Distance: <strong>${dist} meters</strong>${estMin}`;
        
        if (r.turn_by_turn && r.turn_by_turn.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.turn_by_turn.map(step => `
                <div style="margin-bottom: 0.3rem;">🚶 ${step}</div>
            `).join("");
        } else if (r.path_landmarks && r.path_landmarks.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.path_landmarks.map((step, idx) => `
                <div style="margin-bottom: 0.3rem;">[${idx + 1}] ${step.name}</div>
            `).join("");
        } else if (r.path && r.path.length > 0) {
            document.getElementById("navStepsContainer").innerHTML = r.path.map((step, idx) => `
                <div style="margin-bottom: 0.3rem;">[${idx + 1}] ${step.name || step}</div>
            `).join("");
        }

        const nodeIds = r.path_node_ids || (r.path ? r.path.map(s => s.node_id || s) : []);
        currentRouteNodeIds = new Set(nodeIds);
        renderSvgMap();
    })
    .catch(err => console.error(err));
}

// ----------------------------------------------------------------------------
// 7. BENCHMARKS & STATISTICAL ANALYTICS CONTROLLER
// ----------------------------------------------------------------------------

function loadLiveBenchmarks() {
    const intBox = document.getElementById("benchIntervalResult");
    const heapBox = document.getElementById("benchHeapResult");

    if (intBox) intBox.innerHTML = `Running benchmarks on Python backend...`;
    if (heapBox) heapBox.innerHTML = `Running benchmarks on Python backend...`;

    fetch("/api/benchmarks")
        .then(res => res.json())
        .then(data => {
            if (intBox && data.interval_tree) {
                const it = data.interval_tree;
                intBox.innerHTML = `
                    • Dataset Size: <strong>${it.n.toLocaleString()} intervals</strong><br>
                    • AVL Interval Tree Query: <span style="color:var(--accent-emerald); font-weight:700;">${it.tree_time_ms} ms</span><br>
                    • Linear List Scan: <span style="color:var(--accent-rose);">${it.linear_time_ms} ms</span><br>
                    • Performance Speedup: <strong style="color:var(--accent-cyan); font-size:1.1rem;">${it.speedup}× faster</strong>
                `;
            }

            if (heapBox && data.max_heap) {
                const mh = data.max_heap;
                heapBox.innerHTML = `
                    • Dataset Size: <strong>${mh.n.toLocaleString()} priority items</strong><br>
                    • Binary Max-Heap Extract-Max: <span style="color:var(--accent-emerald); font-weight:700;">${mh.heap_time_ms} ms</span><br>
                    • Unsorted List Scan: <span style="color:var(--accent-rose);">${mh.list_time_ms} ms</span><br>
                    • Performance Speedup: <strong style="color:var(--accent-cyan); font-size:1.1rem;">${mh.speedup}× faster</strong>
                `;
            }
        });
}

function renderAnalyticsTable(venues) {
    const tbody = document.getElementById("analyticsVenueTable");
    if (!tbody) return;

    tbody.innerHTML = venues.map(v => `
        <tr>
            <td><strong>${v.name}</strong></td>
            <td>${v.building}</td>
            <td><span class="badge badge-purple">${v.category}</span></td>
            <td><span class="badge badge-cyan">${v.capacity}</span></td>
            <td>${v.air_conditioned ? '✓ Yes' : '—'}</td>
            <td>${v.projector ? '✓ Yes' : '—'}</td>
            <td>${v.sound_system || 'Standard'}</td>
            <td>${v.wheelchair_accessible ? '♿ Accessible' : 'Stairs Only'}</td>
        </tr>
    `).join("");
}

// ----------------------------------------------------------------------------
