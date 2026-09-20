<script setup>
import { CalendarDays, CircleUserRound, FileText, House } from "lucide-vue-next";
import { nextTick, onMounted, ref } from "vue";

import AppointmentForm from "../components/AppointmentForm.vue";
import BaseModal from "../components/BaseModal.vue";
import DoctorAccount from "../components/doctor/DoctorAccount.vue";
import PortalHeader from "../components/PortalHeader.vue";
import PortalSidebar from "../components/PortalSidebar.vue";
import PatientOverview from "../components/patient/PatientOverview.vue";
import PatientRecords from "../components/patient/PatientRecords.vue";
import PatientVisits from "../components/patient/PatientVisits.vue";
import { apiRequest, refreshSession, session, signOut } from "../services/api";
import { dashboardPath, navigate } from "../router";
import { consumeQueuedToast, queueToast, showToast } from "../services/toast";

const loading = ref(true);
const activePanel = ref("patientOverview");
const appointments = ref([]);
const records = ref([]);
const services = ref([]);
const availability = ref([]);
const clinicDoctor = ref("");
const bookingOpen = ref(false);
const bookingBusy = ref(false);
const highlightedId = ref("");

const navItems = [
  { id: "patientOverview", label: "Overview", icon: House },
  { id: "patientSchedule", label: "Appointments", shortLabel: "Visits", icon: CalendarDays },
  { id: "patientRecords", label: "Records", icon: FileText },
  { id: "patientProfile", label: "Account", icon: CircleUserRound },
];

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

async function openNotification(item) {
  activePanel.value = item.entity_type === "appointment" ? "patientSchedule" : "patientRecords";
  highlightedId.value = item.entity_id || "";
  await nextTick();
  const target = document.querySelector(`[data-entity-id="${CSS.escape(highlightedId.value)}"]`);
  target?.scrollIntoView({ behavior: "smooth", block: "center" });
  window.setTimeout(() => {
    highlightedId.value = "";
  }, 3000);
}

async function openAppointment(item) {
  activePanel.value = "patientSchedule";
  highlightedId.value = item?.id || "";
  if (!highlightedId.value) return;
  await nextTick();
  document
    .querySelector(`[data-entity-id="${CSS.escape(highlightedId.value)}"]`)
    ?.scrollIntoView({ behavior: "smooth", block: "center" });
  window.setTimeout(() => {
    highlightedId.value = "";
  }, 3000);
}

function openPublicServices() {
  navigate("/#services");
  nextTick(() => {
    document.getElementById("services")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
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
        <PortalHeader mode="patient" @open-notification="openNotification" />
        <section class="portal-main" aria-label="Patient dashboard">
          <div v-if="loading" class="loading-state">Loading your care information...</div>

          <PatientOverview
            v-else-if="activePanel === 'patientOverview'"
            :appointments="appointments"
            :records="records"
            :highlighted-id="highlightedId"
            @book="bookingOpen = true"
            @open-appointments="openAppointment"
            @open-records="activePanel = 'patientRecords'"
            @open-profile="activePanel = 'patientProfile'"
            @open-services="openPublicServices"
          />

          <PatientVisits
            v-else-if="activePanel === 'patientSchedule'"
            :appointments="appointments"
            :services="services"
            :highlighted-id="highlightedId"
            @book="bookingOpen = true"
            @cancel="cancelAppointment"
          />

          <PatientRecords
            v-else-if="activePanel === 'patientRecords'"
            :records="records"
            :appointments="appointments"
            :highlighted-id="highlightedId"
          />

          <DoctorAccount v-else mode="patient" />
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
