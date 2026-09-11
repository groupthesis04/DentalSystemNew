<script setup>
import { computed, reactive, ref, watch } from "vue";

import ActionIconButton from "../ActionIconButton.vue";
import BaseModal from "../BaseModal.vue";
import StatusBadge from "../StatusBadge.vue";
import { apiRequest, session } from "../../services/api";
import { formatDate, localDateIso } from "../../services/format";
import { showToast } from "../../services/toast";
import { validatedPayload } from "../../services/validation";

const props = defineProps({
  state: { type: Object, required: true },
  highlightedId: { type: String, default: "" },
});
const emit = defineEmits(["refresh", "status-change"]);
const today = localDateIso();
const currentMonth = today.slice(0, 7);
const month = ref(currentMonth);
const selectedDates = ref(new Set());
const schedule = reactive({ time_in: "08:00", time_out: "17:00", interval: "30", _website: "" });
const allOpen = ref(false);
const editorOpen = ref(false);
const editor = reactive({ id: "", doctor: "", date: "", time: "", _website: "" });
const busy = ref(false);

const calendarCells = computed(() => {
  const [year, monthNumber] = month.value.split("-").map(Number);
  const firstWeekday = new Date(year, monthNumber - 1, 1).getDay();
  const count = new Date(year, monthNumber, 0).getDate();
  return [
    ...Array.from({ length: firstWeekday }, (_, index) => ({ spacer: true, key: `s${index}` })),
    ...Array.from({ length: count }, (_, index) => {
      const day = index + 1;
      const date = `${month.value}-${String(day).padStart(2, "0")}`;
      return {
        day,
        date,
        key: date,
        disabled: date < today,
        hasSlots: props.state.availability.some((slot) => slot.date === date),
      };
    }),
  ];
});
const sortedAvailability = computed(() =>
  [...props.state.availability].sort((a, b) =>
    `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`),
  ),
);
const sortedAppointments = computed(() =>
  [...props.state.appointments].sort((a, b) =>
    `${b.created_at || ""} ${b.date} ${b.time}`.localeCompare(
      `${a.created_at || ""} ${a.date} ${a.time}`,
    ),
  ),
);

watch(month, () => {
  selectedDates.value = new Set();
});

function toggleDate(cell) {
  if (cell.disabled || cell.spacer) return;
  const next = new Set(selectedDates.value);
  if (next.has(cell.date)) next.delete(cell.date);
  else next.add(cell.date);
  selectedDates.value = next;
}

function slotLocked(slot) {
  return Boolean(slot.booked || Number(slot.pending_count || 0));
}
function slotStatus(slot) {
  if (slot.booked) return "approved";
  if (Number(slot.pending_count || 0)) return "pending";
  return "completed";
}
function slotStatusText(slot) {
  if (slot.booked) return "Accepted";
  if (Number(slot.pending_count || 0)) return `${slot.pending_count} Pending`;
  return "Open";
}

async function createSchedule() {
  busy.value = true;
  try {
    const payload = validatedPayload({
      doctor: session.user?.name || props.state.clinicDoctor,
      dates: [...selectedDates.value].sort().join(","),
      time_in: schedule.time_in,
      time_out: schedule.time_out,
      interval: schedule.interval,
      _website: schedule._website,
    });
    if (!payload.dates) throw new Error("Select at least one available date.");
    const data = await apiRequest("/api/availability", { method: "POST", body: payload });
    props.state.availability.push(...(data.availability_created || [data.availability]));
    selectedDates.value = new Set();
    showToast(
      `${data.created_count || 1} appointment slot${data.created_count === 1 ? "" : "s"} created.`,
    );
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    busy.value = false;
  }
}

function openEditor(slot) {
  if (slotLocked(slot)) return;
  Object.assign(editor, {
    id: slot.id,
    doctor: slot.doctor,
    date: slot.date,
    time: slot.time,
    _website: "",
  });
  allOpen.value = false;
  editorOpen.value = true;
}

async function saveEditor() {
  busy.value = true;
  try {
    const payload = validatedPayload({ ...editor });
    const data = await apiRequest("/api/availability", { method: "PATCH", body: payload });
    const index = props.state.availability.findIndex((slot) => slot.id === data.availability.id);
    if (index >= 0)
      props.state.availability.splice(index, 1, {
        ...props.state.availability[index],
        ...data.availability,
      });
    editorOpen.value = false;
    showToast("Availability updated.");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    busy.value = false;
  }
}

async function deleteSlot(slot) {
  if (
    slotLocked(slot) ||
    !window.confirm(`Delete availability on ${formatDate(slot.date)} at ${slot.time}?`)
  )
    return;
  try {
    await apiRequest("/api/availability", { method: "DELETE", body: { id: slot.id } });
    const index = props.state.availability.findIndex((item) => item.id === slot.id);
    if (index >= 0) props.state.availability.splice(index, 1);
    showToast("Availability deleted.");
  } catch (error) {
    showToast(error.message, "error");
  }
}
</script>

<template>
  <section class="workspace-panel">
    <div class="schedule-management-grid">
      <section class="dashboard-panel availability-manager">
        <div class="panel-heading inline">
          <div>
            <span class="section-kicker">Admin Control</span>
            <h2>Clinic availability</h2>
          </div>
        </div>
        <form class="stacked-form availability-form" @submit.prevent="createSchedule">
          <label class="hp-field" aria-hidden="true"
            >Website<input v-model="schedule._website" tabindex="-1"
          /></label>
          <div class="availability-scheduler-grid">
            <div class="availability-settings">
              <label
                >Dentist<input
                  :value="session.user?.name || state.clinicDoctor"
                  readonly
                  required /></label
              ><label
                >Schedule month<input v-model="month" type="month" :min="currentMonth" required
              /></label>
              <div class="form-grid availability-time-grid">
                <label
                  >Time in<input
                    v-model="schedule.time_in"
                    type="time"
                    step="900"
                    required /></label
                ><label
                  >Time out<input
                    v-model="schedule.time_out"
                    type="time"
                    step="900"
                    required /></label
                ><label
                  >Slot interval<select v-model="schedule.interval">
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="60">60 minutes</option>
                  </select></label
                >
              </div>
            </div>
            <fieldset class="availability-calendar-fieldset">
              <legend>
                <span>Available dates</span
                ><output
                  >{{ selectedDates.size }} date{{
                    selectedDates.size === 1 ? "" : "s"
                  }}
                  selected</output
                >
              </legend>
              <div class="availability-weekdays">
                <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span
                ><span>Fri</span><span>Sat</span>
              </div>
              <div class="availability-calendar" role="group" aria-label="Select available dates">
                <span
                  v-for="cell in calendarCells.filter((item) => item.spacer)"
                  :key="cell.key"
                  class="availability-calendar-spacer"
                ></span
                ><template
                  v-for="cell in calendarCells.filter((item) => !item.spacer)"
                  :key="cell.key"
                  ><button
                    class="availability-day"
                    :class="{ selected: selectedDates.has(cell.date), 'has-slots': cell.hasSlots }"
                    type="button"
                    :disabled="cell.disabled"
                    :aria-pressed="selectedDates.has(cell.date)"
                    @click="toggleDate(cell)"
                  >
                    <span>{{ cell.day }}</span>
                  </button></template
                >
              </div>
            </fieldset>
          </div>
          <div class="crud-dialog-actions availability-form-actions">
            <button class="secondary-button" type="button" @click="selectedDates = new Set()">
              Clear Dates</button
            ><button class="primary-button" type="submit" :disabled="busy">
              {{ busy ? "Creating..." : "Create Schedule" }}
            </button>
          </div>
        </form>
        <div class="table-wrap compact-table-wrap">
          <table class="crud-table availability-table">
            <thead>
              <tr>
                <th>Dentist</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in sortedAvailability.slice(0, 5)" :key="slot.id">
                <td>
                  <strong>{{ slot.doctor }}</strong>
                </td>
                <td>{{ formatDate(slot.date) }}</td>
                <td>{{ slot.time }}</td>
                <td>
                  <span class="status" :class="slotStatus(slot)">{{ slotStatusText(slot) }}</span>
                </td>
                <td>
                  <div class="table-actions">
                    <ActionIconButton
                      action="edit"
                      label="Edit availability"
                      :disabled="slotLocked(slot)"
                      @click="openEditor(slot)"
                    /><ActionIconButton
                      action="delete"
                      label="Delete availability"
                      :disabled="slotLocked(slot)"
                      @click="deleteSlot(slot)"
                    />
                  </div>
                </td>
              </tr>
              <tr v-if="!sortedAvailability.length">
                <td colspan="5" class="table-empty">No clinic availability has been added.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="sortedAvailability.length > 5" class="availability-list-footer">
          <button
            id="openAvailabilityListDialog"
            class="secondary-button"
            type="button"
            @click="allOpen = true"
          >
            More
          </button>
        </div>
      </section>

      <section class="dashboard-panel">
        <div class="panel-heading inline">
          <div>
            <span class="section-kicker">Patient Bookings</span>
            <h2>Appointment schedule</h2>
          </div>
          <button class="secondary-button" type="button" @click="emit('refresh')">Refresh</button>
        </div>
        <div class="table-wrap">
          <table class="crud-table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Service</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in sortedAppointments"
                :key="item.id"
                :data-entity-id="item.id"
                :class="{ 'notification-target-glow': highlightedId === item.id }"
              >
                <td>
                  <strong>{{ item.patient_name }}</strong>
                  <div class="meta">{{ item.patient_email }}</div>
                </td>
                <td>{{ item.service }}</td>
                <td>{{ formatDate(item.date) }}</td>
                <td>{{ item.time }}</td>
                <td>
                  <select
                    class="status-select"
                    :class="item.status"
                    :value="item.status"
                    @change="emit('status-change', item, $event.target.value)"
                  >
                    <option value="pending">Pending</option>
                    <option value="approved">Accepted</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </td>
              </tr>
              <tr v-if="!sortedAppointments.length">
                <td colspan="5">No appointments yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <BaseModal
      v-if="allOpen"
      title="All Clinic Availability"
      eyebrow="Admin Control"
      size-class="availability-list-dialog"
      @close="allOpen = false"
      ><div class="availability-list-dialog-body">
        <div class="table-wrap">
          <table class="crud-table availability-table">
            <thead>
              <tr>
                <th>Dentist</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in sortedAvailability" :key="slot.id">
                <td>
                  <strong>{{ slot.doctor }}</strong>
                </td>
                <td>{{ formatDate(slot.date) }}</td>
                <td>{{ slot.time }}</td>
                <td>
                  <span class="status" :class="slotStatus(slot)">{{ slotStatusText(slot) }}</span>
                </td>
                <td>
                  <div class="table-actions">
                    <ActionIconButton
                      action="edit"
                      label="Edit availability"
                      :disabled="slotLocked(slot)"
                      @click="openEditor(slot)"
                    /><ActionIconButton
                      action="delete"
                      label="Delete availability"
                      :disabled="slotLocked(slot)"
                      @click="deleteSlot(slot)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="crud-dialog-actions">
          <button class="secondary-button" type="button" @click="allOpen = false">Close</button>
        </div>
      </div></BaseModal
    >

    <BaseModal
      v-if="editorOpen"
      title="Edit Availability"
      eyebrow="Time slot"
      size-class="availability-editor-dialog"
      @close="editorOpen = false"
      ><form class="stacked-form" @submit.prevent="saveEditor">
        <label class="hp-field" aria-hidden="true"
          >Website<input v-model="editor._website" tabindex="-1" /></label
        ><label>Dentist<input v-model="editor.doctor" readonly required /></label>
        <div class="form-grid two">
          <label
            >Available date<input v-model="editor.date" type="date" :min="today" required /></label
          ><label
            >Available time<input v-model="editor.time" type="time" step="300" required
          /></label>
        </div>
        <div class="crud-dialog-actions">
          <button class="secondary-button" type="button" @click="editorOpen = false">Cancel</button
          ><button class="primary-button" type="submit" :disabled="busy">
            {{ busy ? "Saving..." : "Save Changes" }}
          </button>
        </div>
      </form></BaseModal
    >
  </section>
</template>
