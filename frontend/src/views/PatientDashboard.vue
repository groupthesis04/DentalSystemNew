<script setup>
import {
  CalendarDays,
  CircleDollarSign,
  CircleUserRound,
  ClipboardList,
  HeartPulse,
} from "lucide-vue-next";
import { computed, nextTick, onMounted, reactive, ref } from "vue";

import AppointmentForm from "../components/AppointmentForm.vue";
import AvatarBadge from "../components/AvatarBadge.vue";
import BaseModal from "../components/BaseModal.vue";
import PortalHeader from "../components/PortalHeader.vue";
import PortalSidebar from "../components/PortalSidebar.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { apiRequest, refreshSession, session, signOut } from "../services/api";
import {
  formatDate,
  formatDateTime,
  formatMoney,
  treatmentBalance,
  treatmentProcedure,
} from "../services/format";
import { dashboardPath, navigate } from "../router";
import { consumeQueuedToast, queueToast, showToast } from "../services/toast";
import { imageToDataUrl, validatedPayload } from "../services/validation";

// Lists from the API plus the user's current selections and open dialogs.
const loading = ref(true);
const activePanel = ref("patientOverview");
const appointments = ref([]);
const records = ref([]);
const services = ref([]);
const availability = ref([]);
const clinicDoctor = ref("");
const bookingOpen = ref(false);
const bookingBusy = ref(false);
const profileBusy = ref(false);
const profileForm = reactive({ name: "", email: "", phone: "", profile_image: "", _website: "" });
const highlightedId = ref("");

const navItems = [
  { id: "patientOverview", label: "My Care", shortLabel: "Home", icon: HeartPulse },
  { id: "patientSchedule", label: "Appointments", shortLabel: "Visits", icon: CalendarDays },
  { id: "patientProfile", label: "Account", icon: CircleUserRound },
];

// Dashboard summaries are calculated from appointments and treatment records.
const nextVisit = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  return [...appointments.value]
    .filter((item) => item.date >= today && ["pending", "approved"].includes(item.status))
    .sort((a, b) => `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`))[0];
});
const outstandingBalance = computed(() =>
  records.value.reduce((sum, record) => sum + treatmentBalance(record), 0),
);
const completedVisits = computed(
  () => appointments.value.filter((item) => item.status === "completed").length,
);
function hydrateProfile() {
  Object.assign(profileForm, {
    name: session.user?.name || "",
    email: session.user?.email || "",
    phone: session.user?.phone || "",
    profile_image: session.user?.profile_image || "",
    _website: "",
  });
}

// Fetch dashboard information together so the page has one loading state.
async function loadData() {
  const [appointmentData, recordData, serviceData, availabilityData] = await Promise.all([
    apiRequest("/api/appointments"),
    apiRequest("/api/records"),
    apiRequest("/api/services"),
    apiRequest("/api/availability"),
  ]);
  appointments.value = appointmentData.appointments || [];
  records.value = recordData.records || [];
  services.value = serviceData.services || [];
  availability.value = availabilityData.availability || [];
  clinicDoctor.value = availabilityData.clinic_doctor || availability.value[0]?.doctor || "";
}

async function logout() {
  try {
    await signOut();
    queueToast("Logged out.");
    navigate("/");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function cancelAppointment(item) {
  if (!window.confirm(`Cancel the ${item.service} appointment?`)) return;
  try {
    const data = await apiRequest("/api/appointments", {
      method: "PATCH",
      body: { id: item.id, status: "cancelled" },
    });
    const index = appointments.value.findIndex((entry) => entry.id === item.id);
    if (index >= 0) appointments.value.splice(index, 1, data.appointment);
    showToast("Appointment cancelled.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function appointmentCreated(item) {
  appointments.value.unshift(item);
  bookingOpen.value = false;
  await loadData();
}

async function updateProfile() {
  profileBusy.value = true;
  try {
    const payload = validatedPayload({ ...profileForm });
    const data = await apiRequest("/api/profile", { method: "PATCH", body: payload });
    session.user = data.user;
    hydrateProfile();
    showToast("Profile updated.");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    profileBusy.value = false;
  }
}

async function chooseProfileImage(event) {
  try {
    profileForm.profile_image = await imageToDataUrl(event.target.files?.[0]);
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function openNotification(item) {
  activePanel.value = item.entity_type === "appointment" ? "patientSchedule" : "patientOverview";
  highlightedId.value = item.entity_id || "";
  await nextTick();
  const target = document.querySelector(`[data-entity-id="${CSS.escape(highlightedId.value)}"]`);
  target?.scrollIntoView({ behavior: "smooth", block: "center" });
  window.setTimeout(() => {
    highlightedId.value = "";
  }, 3000);
}

// Confirm the account before displaying private patient information.
onMounted(async () => {
  document.title = "Patient Dashboard - BORJA Dental Clinic";
  consumeQueuedToast();
  try {
    const user = await refreshSession();
    if (!user) {
      queueToast("Please log in to continue.", "error");
      navigate("/?login=1");
      return;
    }
    if (user.role !== "patient") {
      navigate(dashboardPath(user.role));
      return;
    }
    hydrateProfile();
    await loadData();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <template v-if="session.user">
    <main class="portal-page patient-portal">
      <PortalSidebar
        :user="session.user"
        role-label="Patient"
        :items="navItems"
        :active="activePanel"
        @select="activePanel = $event"
        @logout="logout"
      />
      <div class="portal-workspace">
        <PortalHeader
          mode="patient"
          title="Patient Portal"
          subtitle="Appointments and dental records"
          @open-notification="openNotification"
        />
        <section class="portal-main" aria-label="Patient dashboard">
          <div v-if="loading" class="loading-state">Loading your care information...</div>

          <section v-else-if="activePanel === 'patientOverview'" class="workspace-panel">
            <section class="dashboard-analytics-banner patient-dashboard-banner">
              <div class="analytics-banner-copy">
                <span>Patient Dashboard</span>
                <h1>My Dental Care</h1>
                <p>Appointments, treatments, and account information in one place.</p>
              </div>
              <div class="analytics-banner-side">
                <div class="analytics-account">
                  <AvatarBadge :name="session.user.name" :image="session.user.profile_image" /><span
                    ><strong>{{ session.user.name }}</strong
                    ><small>{{ session.user.email }}</small></span
                  >
                </div>
                <button class="banner-primary-action" type="button" @click="bookingOpen = true">
                  Book appointment
                </button>
              </div>
            </section>

            <section
              class="analytics-metric-grid patient-summary-grid"
              aria-label="Patient care summary"
            >
              <article class="dashboard-color-card metric-next-visit">
                <header>
                  <span>Next Visit</span><CalendarDays :size="22" aria-hidden="true" />
                </header>
                <strong>{{
                  nextVisit
                    ? `${formatDate(nextVisit.date)} at ${nextVisit.time}`
                    : "No appointment yet"
                }}</strong
                ><small>{{
                  nextVisit
                    ? `${nextVisit.service} with ${nextVisit.doctor}`
                    : "Book a visit when you are ready"
                }}</small>
              </article>
              <article class="dashboard-color-card metric-patients">
                <header>
                  <span>Appointments</span><CalendarDays :size="22" aria-hidden="true" />
                </header>
                <strong>{{ appointments.length }}</strong
                ><small>All scheduled visits</small>
                <div class="color-card-breakdown compact">
                  <span
                    >Completed <strong>{{ completedVisits }}</strong></span
                  ><span
                    >Upcoming <strong>{{ nextVisit ? 1 : 0 }}</strong></span
                  >
                </div>
              </article>
              <article class="dashboard-color-card metric-appointments">
                <header>
                  <span>Dental Records</span><ClipboardList :size="22" aria-hidden="true" />
                </header>
                <strong>{{ records.length }}</strong
                ><small>Treatments recorded by the clinic</small>
              </article>
              <article class="dashboard-color-card metric-reviews">
                <header>
                  <span>Outstanding Balance</span><CircleDollarSign :size="22" aria-hidden="true" />
                </header>
                <strong>{{ formatMoney(outstandingBalance) }}</strong
                ><small>Remaining treatment balance</small>
              </article>
            </section>

            <div class="dashboard-section-heading">
              <div>
                <h2>My Care</h2>
                <p>Review appointments and treatment history.</p>
              </div>
            </div>
            <div class="patient-layout">
              <section class="dashboard-panel">
                <div class="panel-heading inline">
                  <div>
                    <span class="section-kicker">Read / Update</span>
                    <h3>My appointments</h3>
                  </div>
                  <button class="secondary-button" type="button" @click="bookingOpen = true">
                    Book New
                  </button>
                </div>
                <div class="table-wrap">
                  <table class="crud-table patient-appointment-table">
                    <thead>
                      <tr>
                        <th>Service</th>
                        <th>Dentist</th>
                        <th>Date &amp; Time</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="item in appointments"
                        :key="item.id"
                        :data-entity-id="item.id"
                        :class="{ 'notification-target-glow': highlightedId === item.id }"
                      >
                        <td>
                          <strong>{{ item.service }}</strong>
                          <div v-if="item.notes" class="meta">{{ item.notes }}</div>
                        </td>
                        <td>{{ item.doctor }}</td>
                        <td>
                          {{ formatDate(item.date) }}
                          <div class="meta">{{ item.time }}</div>
                        </td>
                        <td><StatusBadge :status="item.status" /></td>
                        <td>
                          <button
                            v-if="!['cancelled', 'completed'].includes(item.status)"
                            class="danger-button compact-button"
                            type="button"
                            @click="cancelAppointment(item)"
                          >
                            Cancel</button
                          ><span v-else class="meta">No action</span>
                        </td>
                      </tr>
                      <tr v-if="!appointments.length">
                        <td colspan="5" class="table-empty">No appointments yet.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>
              <section class="dashboard-panel">
                <div class="panel-heading inline">
                  <div>
                    <span class="section-kicker">Read</span>
                    <h3>Dental history</h3>
                  </div>
                </div>
                <div class="table-wrap">
                  <table class="crud-table patient-record-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Procedure</th>
                        <th>Tooth No./s</th>
                        <th>Dentist</th>
                        <th>Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="record in records"
                        :key="record.id"
                        :data-entity-id="record.id"
                        :class="{ 'notification-target-glow': highlightedId === record.id }"
                      >
                        <td>{{ formatDate(record.treatment_date) }}</td>
                        <td>
                          <strong>{{ treatmentProcedure(record) }}</strong>
                          <div v-if="record.remarks || record.notes" class="meta">
                            {{ record.remarks || record.notes }}
                          </div>
                        </td>
                        <td>{{ record.tooth_numbers || "-" }}</td>
                        <td>{{ record.doctor_name || "Dentist" }}</td>
                        <td>{{ formatMoney(treatmentBalance(record)) }}</td>
                      </tr>
                      <tr v-if="!records.length">
                        <td colspan="5" class="table-empty">
                          No dental records have been added yet.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          </section>

          <section v-else-if="activePanel === 'patientSchedule'" class="workspace-panel">
            <div class="dashboard-panel">
              <div class="panel-heading inline">
                <div>
                  <span class="section-kicker">Appointments</span>
                  <h2>My schedule</h2>
                </div>
                <button class="secondary-button" type="button" @click="bookingOpen = true">
                  Book New
                </button>
              </div>
              <div class="table-wrap">
                <table class="crud-table">
                  <thead>
                    <tr>
                      <th>Service</th>
                      <th>Dentist</th>
                      <th>Date &amp; Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in appointments"
                      :key="item.id"
                      :data-entity-id="item.id"
                      :class="{ 'notification-target-glow': highlightedId === item.id }"
                    >
                      <td>
                        <strong>{{ item.service }}</strong>
                      </td>
                      <td>{{ item.doctor }}</td>
                      <td>
                        {{ formatDate(item.date) }}
                        <div class="meta">{{ item.time }}</div>
                      </td>
                      <td><StatusBadge :status="item.status" /></td>
                      <td>
                        <button
                          v-if="!['cancelled', 'completed'].includes(item.status)"
                          class="danger-button compact-button"
                          type="button"
                          @click="cancelAppointment(item)"
                        >
                          Cancel</button
                        ><span v-else class="meta">No action</span>
                      </td>
                    </tr>
                    <tr v-if="!appointments.length">
                      <td colspan="5" class="table-empty">No appointments yet.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <section v-else class="workspace-panel">
            <div class="dashboard-panel">
              <div class="panel-heading inline"><h2>Profile</h2></div>
              <form class="stacked-form profile-edit-form" @submit.prevent="updateProfile">
                <label class="hp-field" aria-hidden="true"
                  >Website<input v-model="profileForm._website" tabindex="-1" /></label
                ><label
                  >Full name<input
                    v-model="profileForm.name"
                    autocomplete="name"
                    minlength="2"
                    maxlength="120"
                    required /></label
                ><label
                  >Email<input
                    v-model="profileForm.email"
                    type="email"
                    autocomplete="email"
                    maxlength="254"
                    required /></label
                ><label
                  >Phone<input
                    v-model="profileForm.phone"
                    autocomplete="tel"
                    maxlength="24" /></label
                ><label
                  >Profile picture<input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    @change="chooseProfileImage" /></label
                ><button class="primary-button full" type="submit" :disabled="profileBusy">
                  {{ profileBusy ? "Saving..." : "Save Profile" }}
                </button>
              </form>
              <div class="detail-grid">
                <span
                  ><strong>{{ session.user.name }}</strong
                  >Name</span
                ><span
                  ><strong>{{ session.user.email }}</strong
                  >Email</span
                ><span
                  ><strong>{{ session.user.phone || "Not provided" }}</strong
                  >Phone</span
                ><span
                  ><strong>{{ formatDateTime(session.user.created_at) }}</strong
                  >Member since</span
                >
              </div>
            </div>
          </section>
        </section>
      </div>
    </main>

    <BaseModal
      v-if="bookingOpen"
      title="Book a New Appointment"
      eyebrow="Create Appointment"
      size-class="appointment-booking-dialog"
      @close="bookingOpen = false"
    >
      <AppointmentForm
        v-model:busy="bookingBusy"
        compact
        :services="services"
        :availability="availability"
        :clinic-doctor="clinicDoctor"
        @created="appointmentCreated"
        @cancel="bookingOpen = false"
      />
    </BaseModal>
  </template>
  <div v-else class="loading-state">Opening your dashboard...</div>
</template>
