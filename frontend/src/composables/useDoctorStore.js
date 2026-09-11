import { reactive } from "vue";

import { apiRequest } from "../services/api";

export function useDoctorStore() {
  const state = reactive({
    appointments: [],
    records: [],
    patients: [],
    feedback: [],
    services: [],
    promos: [],
    availability: [],
    clinicDoctor: "",
    loading: false,
  });

  async function load() {
    state.loading = true;
    try {
      const [appointments, records, patients, feedback, services, promos, availability] =
        await Promise.all([
          apiRequest("/api/appointments"),
          apiRequest("/api/records"),
          apiRequest("/api/patients"),
          apiRequest("/api/feedback"),
          apiRequest("/api/services"),
          apiRequest("/api/promos"),
          apiRequest("/api/availability"),
        ]);
      state.appointments = appointments.appointments || [];
      state.records = records.records || [];
      state.patients = patients.patients || [];
      state.feedback = feedback.feedback || [];
      state.services = services.services || [];
      state.promos = promos.promos || [];
      state.availability = availability.availability || [];
      state.clinicDoctor = availability.clinic_doctor || state.availability[0]?.doctor || "";
    } finally {
      state.loading = false;
    }
  }

  return { state, load };
}
