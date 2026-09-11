<script setup>
import { computed, reactive, watch } from "vue";
import { CalendarDays, Info } from "lucide-vue-next";

import { apiRequest } from "../services/api";
import { validatedPayload } from "../services/validation";
import { showToast } from "../services/toast";

const props = defineProps({
  services: { type: Array, default: () => [] },
  availability: { type: Array, default: () => [] },
  clinicDoctor: { type: String, default: "" },
  initialService: { type: String, default: "" },
  submitLabel: { type: String, default: "Book Appointment" },
  compact: { type: Boolean, default: false },
});
const emit = defineEmits(["created", "login-required", "cancel"]);

const form = reactive({ service: "", doctor: "", date: "", time: "", notes: "", _website: "" });
const busy = defineModel("busy", { type: Boolean, default: false });
const dates = computed(() => [...new Set(props.availability.map((slot) => slot.date))].sort());
const slots = computed(() =>
  props.availability.filter((slot) => slot.date === form.date && !slot.booked),
);

watch(
  () => props.clinicDoctor,
  (doctor) => {
    form.doctor = doctor || props.availability[0]?.doctor || "";
  },
  { immediate: true },
);
watch(
  () => props.initialService,
  (service) => {
    if (service) form.service = service;
  },
  { immediate: true },
);
watch(
  () => form.date,
  () => {
    form.time = "";
  },
);
watch(
  () => props.availability,
  (items) => {
    if (!form.doctor) form.doctor = props.clinicDoctor || items[0]?.doctor || "";
    if (form.date && !items.some((slot) => slot.date === form.date && slot.time === form.time))
      form.time = "";
  },
  { deep: true },
);

async function submit() {
  busy.value = true;
  try {
    const payload = validatedPayload({ ...form });
    if (!payload.date || !payload.time) throw new Error("Choose an available date and time.");
    const data = await apiRequest("/api/appointments", { method: "POST", body: payload });
    showToast("Appointment request submitted.");
    Object.assign(form, {
      service: "",
      date: "",
      time: "",
      notes: "",
      _website: "",
      doctor: props.clinicDoctor || props.availability[0]?.doctor || "",
    });
    emit("created", data.appointment);
  } catch (error) {
    if (/log in|authentication|session/i.test(error.message)) emit("login-required");
    else showToast(error.message, "error");
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <form
    class="stacked-form"
    :class="{ 'appointment-panel': !compact }"
    aria-label="Appointment booking form"
    @submit.prevent="submit"
  >
    <label class="hp-field" aria-hidden="true"
      >Website<input v-model="form._website" tabindex="-1" autocomplete="off"
    /></label>
    <div v-if="!compact" class="panel-heading">
      <span class="appointment-heading-icon"><CalendarDays :size="24" /></span>
      <div>
        <h2>Book an Appointment</h2>
        <p>Quick and easy scheduling</p>
      </div>
    </div>
    <label
      >Dental service
      <select v-model="form.service" required>
        <option value="">Select service</option>
        <option v-for="service in services" :key="service.id || service.name" :value="service.name">
          {{ service.name }}
        </option>
      </select>
    </label>
    <label class="single-doctor-field"
      >Clinic dentist<input v-model="form.doctor" readonly required
    /></label>
    <div class="form-grid two">
      <label
        >Preferred date
        <select v-model="form.date" required>
          <option value="">Select available date</option>
          <option v-for="date in dates" :key="date" :value="date">{{ date }}</option>
        </select>
      </label>
      <label
        >Preferred time<input v-model="form.time" type="hidden" required /><span
          class="selected-time"
          >{{ form.time || "Select slot" }}</span
        ></label
      >
    </div>
    <div class="booking-time-group">
      <span v-if="compact" class="form-label">Available times</span>
      <div class="time-slots" aria-label="Available appointment times">
        <button
          v-for="slot in slots"
          :key="slot.id"
          class="time-slot"
          type="button"
          :class="{ active: form.time === slot.time }"
          @click="form.time = slot.time"
        >
          {{ slot.time }}
        </button>
        <span v-if="form.date && !slots.length" class="meta"
          >No available times for this date.</span
        >
        <span v-else-if="!form.date" class="meta">Choose a date to view times.</span>
      </div>
    </div>
    <label
      >Notes<textarea
        v-model="form.notes"
        rows="3"
        maxlength="500"
        placeholder="Symptoms, concerns, or preferred details"
      ></textarea>
    </label>
    <div v-if="compact" class="crud-dialog-actions">
      <button class="secondary-button" type="button" @click="emit('cancel')">Cancel</button>
      <button class="primary-button" type="submit" :disabled="busy">
        {{ busy ? "Submitting..." : submitLabel }}
      </button>
    </div>
    <template v-else>
      <button class="primary-button full" type="submit" :disabled="busy">
        {{ busy ? "Submitting..." : submitLabel }}
      </button>
      <div class="booking-note">
        <Info :size="20" />
        <slot name="note" />
      </div>
    </template>
  </form>
</template>
