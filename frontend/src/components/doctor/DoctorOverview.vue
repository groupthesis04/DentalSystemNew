<script setup>
import {
  ArrowRight,
  CalendarDays,
  CircleDollarSign,
  ClipboardList,
  RefreshCw,
  Star,
  Users,
} from "lucide-vue-next";
import { computed, ref } from "vue";

import AvatarBadge from "../AvatarBadge.vue";
import StatusBadge from "../StatusBadge.vue";
import {
  formatDate,
  formatMoney,
  localDateIso,
  treatmentBalance,
  treatmentProcedure,
} from "../../services/format";
import { session } from "../../services/api";

const props = defineProps({
  state: { type: Object, required: true },
  highlightedId: { type: String, default: "" },
});
const emit = defineEmits(["select-panel", "status-change", "refresh"]);

const selectedDate = ref(localDateIso());
const selectedPeriod = ref("month");
const periods = [
  { id: "today", label: "Today" },
  { id: "week", label: "Week" },
  { id: "month", label: "Month" },
  { id: "all", label: "All time" },
];

function isInSelectedPeriod(value) {
  const iso = String(value || "").slice(0, 10);
  if (!iso || selectedPeriod.value === "all") return selectedPeriod.value === "all";

  const today = new Date(`${localDateIso()}T00:00:00`);
  const candidate = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(candidate.getTime())) return false;
  if (selectedPeriod.value === "today") return iso === localDateIso(today);

  if (selectedPeriod.value === "week") {
    const start = new Date(today);
    const mondayOffset = (today.getDay() + 6) % 7;
    start.setDate(today.getDate() - mondayOffset);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return candidate >= start && candidate <= end;
  }

  return (
    candidate.getFullYear() === today.getFullYear() && candidate.getMonth() === today.getMonth()
  );
}

const periodLabel = computed(
  () => periods.find((period) => period.id === selectedPeriod.value)?.label || "Month",
);
const periodRecords = computed(() =>
  props.state.records.filter((record) => isInSelectedPeriod(record.treatment_date)),
);
const periodAppointments = computed(() =>
  props.state.appointments.filter((item) => isInSelectedPeriod(item.date)),
);
const week = computed(() => {
  const basis = new Date(`${selectedDate.value}T00:00:00`);
  const start = new Date(basis);
  start.setDate(start.getDate() - start.getDay());
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    return {
      iso: localDateIso(date),
      day: date.toLocaleDateString(undefined, { weekday: "short" }),
      date: date.getDate(),
    };
  });
});
const dailyAppointments = computed(() =>
  props.state.appointments
    .filter((item) => item.date === selectedDate.value && item.status !== "cancelled")
    .sort((a, b) => a.time.localeCompare(b.time)),
);
const pending = computed(() =>
  props.state.appointments
    .filter((item) => item.status === "pending")
    .sort((a, b) => `${b.date} ${b.time}`.localeCompare(`${a.date} ${a.time}`)),
);
const totals = computed(() =>
  periodRecords.value.reduce(
    (sum, record) => {
      sum.charged += Number(record.amount_charged || 0);
      sum.paid += Number(record.amount_paid || 0);
      sum.balance += treatmentBalance(record);
      return sum;
    },
    { charged: 0, paid: 0, balance: 0 },
  ),
);
const collectionRate = computed(() =>
  totals.value.charged
    ? Math.min(100, Math.round((totals.value.paid / totals.value.charged) * 100))
    : 0,
);
const completedAppointments = computed(
  () => periodAppointments.value.filter((item) => item.status === "completed").length,
);
const serviceTiles = computed(() =>
  props.state.services.slice(0, 7).map((service) => ({
    ...service,
    count: props.state.records.filter((record) => treatmentProcedure(record) === service.name)
      .length,
  })),
);
const incomeMonths = computed(() => {
  const now = new Date();
  const months = Array.from({ length: 12 }, (_, offset) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (11 - offset), 1);
    return {
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`,
      label: date.toLocaleDateString(undefined, { month: "short" }),
      value: 0,
    };
  });
  const map = new Map(months.map((month) => [month.key, month]));
  for (const record of props.state.records) {
    const month = map.get(String(record.treatment_date || "").slice(0, 7));
    if (month) month.value += Number(record.amount_paid || 0);
  }
  const maximum = Math.max(1, ...months.map((month) => month.value));
  return months.map((month) => ({
    ...month,
    height: Math.max(month.value ? 8 : 2, (month.value / maximum) * 100),
  }));
});
const statusCounts = computed(() =>
  ["pending", "approved", "completed", "cancelled"].map((status) => ({
    status,
    label: status === "approved" ? "Accepted" : status[0].toUpperCase() + status.slice(1),
    value: periodAppointments.value.filter((item) => item.status === status).length,
  })),
);
const patientAnalytics = computed(() => {
  const treated = new Set(props.state.records.map((record) => record.patient_id)).size;
  const balances = new Set(
    props.state.records
      .filter((record) => treatmentBalance(record) > 0)
      .map((record) => record.patient_id),
  ).size;
  return [
    { label: "Registered patients", value: props.state.patients.length },
    { label: "With treatment history", value: treated },
    { label: "With outstanding balance", value: balances },
  ];
});

function barWidth(items, value) {
  return `${Math.round((value / Math.max(1, ...items.map((item) => item.value))) * 100)}%`;
}

function tileInitials(name) {
  return String(name)
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}
</script>

<template>
  <section class="workspace-panel clinic-overview">
    <section class="dashboard-analytics-banner">
      <div class="analytics-banner-copy">
        <span>Dashboard</span>
        <h1>Clinic Analytics</h1>
        <p>
          {{
            new Date().toLocaleDateString(undefined, {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            })
          }}
        </p>
      </div>
      <div class="analytics-banner-side">
        <div class="analytics-account">
          <AvatarBadge :name="session.user?.name" :image="session.user?.profile_image" />
          <span
            ><strong>{{ session.user?.name }}</strong
            ><small>Clinic administrator</small></span
          >
        </div>
        <div class="period-tabs" role="group" aria-label="Dashboard reporting period">
          <button
            v-for="period in periods"
            :key="period.id"
            type="button"
            :class="{ active: selectedPeriod === period.id }"
            @click="selectedPeriod = period.id"
          >
            {{ period.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="analytics-metric-grid" aria-label="Clinic summary">
      <article class="dashboard-color-card metric-collections">
        <header>
          <span>Net Collections</span><CircleDollarSign :size="22" aria-hidden="true" />
        </header>
        <strong>{{ formatMoney(totals.paid) }}</strong>
        <small>{{ periodLabel }} treatment payments</small>
        <div class="color-card-breakdown">
          <span
            >Charged <strong>{{ formatMoney(totals.charged) }}</strong></span
          >
          <span
            >Outstanding <strong>{{ formatMoney(totals.balance) }}</strong></span
          >
          <span
            >Collection rate <strong>{{ collectionRate }}%</strong></span
          >
        </div>
        <button
          class="color-card-link"
          type="button"
          @click="emit('select-panel', 'doctorStatistics')"
        >
          Open reports <ArrowRight :size="16" aria-hidden="true" />
        </button>
      </article>

      <article class="dashboard-color-card metric-patients">
        <header><span>Patients</span><Users :size="22" aria-hidden="true" /></header>
        <strong>{{ state.patients.length }}</strong>
        <small>Registered patient records</small>
        <div class="color-card-breakdown compact">
          <span
            >Treated <strong>{{ patientAnalytics[1].value }}</strong></span
          ><span
            >With balance <strong>{{ patientAnalytics[2].value }}</strong></span
          >
        </div>
      </article>

      <article class="dashboard-color-card metric-appointments">
        <header><span>Appointments</span><CalendarDays :size="22" aria-hidden="true" /></header>
        <strong>{{ periodAppointments.length }}</strong>
        <small>{{ periodLabel }} appointment activity</small>
        <div class="color-card-breakdown compact">
          <span
            >Pending <strong>{{ statusCounts[0].value }}</strong></span
          ><span
            >Completed <strong>{{ completedAppointments }}</strong></span
          >
        </div>
      </article>

      <article class="dashboard-color-card metric-treatments">
        <header>
          <span>Treatment Records</span><ClipboardList :size="22" aria-hidden="true" />
        </header>
        <strong>{{ periodRecords.length }}</strong>
        <small>Recorded during {{ periodLabel.toLowerCase() }}</small>
        <div class="color-card-breakdown compact">
          <span
            >Services <strong>{{ state.services.length }}</strong></span
          ><span
            >All records <strong>{{ state.records.length }}</strong></span
          >
        </div>
      </article>

      <article class="dashboard-color-card metric-reviews">
        <header><span>Patient Reviews</span><Star :size="22" aria-hidden="true" /></header>
        <strong>{{ state.feedback.length }}</strong>
        <small>Feedback received by the clinic</small>
        <div class="color-card-breakdown compact">
          <span
            >Completed visits <strong>{{ completedAppointments }}</strong></span
          ><span
            >Pending visits <strong>{{ pending.length }}</strong></span
          >
        </div>
      </article>
    </section>

    <div class="dashboard-section-heading">
      <div>
        <h2>Operations</h2>
        <p>Appointments and requests that need attention.</p>
      </div>
    </div>

    <div class="dashboard-operations-grid">
      <section class="dashboard-panel reference-dashboard-card reference-appointments-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">Daily schedule</span>
            <h2>Appointments</h2>
          </div>
          <div class="schedule-card-tools">
            <label class="reference-date-field"
              ><span>Selected date</span><input v-model="selectedDate" type="date"
            /></label>
            <button
              class="icon-button dashboard-refresh"
              type="button"
              title="Refresh appointments"
              aria-label="Refresh appointments"
              @click="emit('refresh')"
            >
              <RefreshCw :size="18" aria-hidden="true" />
            </button>
          </div>
        </div>
        <div class="dashboard-day-strip" aria-label="Choose appointment date">
          <button
            v-for="day in week"
            :key="day.iso"
            class="dashboard-day-button"
            :class="{ active: day.iso === selectedDate }"
            type="button"
            @click="selectedDate = day.iso"
          >
            <span>{{ day.day }}</span
            ><strong>{{ day.date }}</strong>
          </button>
        </div>
        <div class="reference-appointment-strip">
          <article
            v-for="item in dailyAppointments"
            :key="item.id"
            class="reference-appointment-card"
            :class="{ 'notification-target-glow': highlightedId === item.id }"
            :data-entity-id="item.id"
          >
            <span class="reference-appointment-avatar" aria-hidden="true">{{
              tileInitials(item.patient_name)
            }}</span
            ><strong>{{ item.patient_name }}</strong
            ><span>{{ item.service }}</span
            ><time>{{ item.time }}</time
            ><StatusBadge :status="item.status" />
          </article>
          <p v-if="!dailyAppointments.length" class="dashboard-empty">
            No appointments scheduled for this date.
          </p>
        </div>
      </section>

      <section class="dashboard-panel reference-dashboard-card request-queue-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">Action required</span>
            <h2>Appointment Requests</h2>
          </div>
          <span class="panel-count">{{ pending.length }} pending</span>
        </div>
        <div class="pending-appointment-list">
          <article
            v-for="item in pending.slice(0, 5)"
            :key="item.id"
            class="pending-appointment-card"
            :data-entity-id="item.id"
            :class="{ 'notification-target-glow': highlightedId === item.id }"
          >
            <div>
              <h3>{{ item.patient_name }}</h3>
              <p>{{ item.service }} | {{ formatDate(item.date) }} at {{ item.time }}</p>
            </div>
            <div class="appointment-decision-actions">
              <button
                class="appointment-accept appointment-decision"
                type="button"
                @click="emit('status-change', item, 'approved')"
              >
                Accept</button
              ><button
                class="appointment-decline appointment-decision"
                type="button"
                @click="emit('status-change', item, 'cancelled')"
              >
                Decline
              </button>
            </div>
          </article>
          <p v-if="!pending.length" class="dashboard-empty">No appointment requests are waiting.</p>
        </div>
        <button
          class="secondary-button full queue-view-button"
          type="button"
          @click="emit('select-panel', 'doctorSchedule')"
        >
          View full schedule
        </button>
      </section>
    </div>

    <div class="dashboard-section-heading">
      <div>
        <h2>Services</h2>
        <p>Quick access to the clinic treatment catalog.</p>
      </div>
      <button class="text-link" type="button" @click="emit('select-panel', 'doctorSettings')">
        Manage services
      </button>
    </div>

    <section class="dashboard-panel reference-dashboard-card service-overview-card">
      <div class="treatment-tile-grid">
        <button
          v-for="service in serviceTiles"
          :key="service.id"
          class="treatment-tile"
          type="button"
          @click="emit('select-panel', 'doctorPatients')"
        >
          <span class="treatment-tile-icon">{{ tileInitials(service.name) }}</span
          ><strong>{{ service.name }}</strong
          ><small>{{ service.count }} treatment{{ service.count === 1 ? "" : "s" }}</small>
        </button>
        <p v-if="!serviceTiles.length" class="dashboard-empty">
          No dental services have been added.
        </p>
      </div>
    </section>

    <div class="dashboard-section-heading">
      <div>
        <h2>Insights</h2>
        <p>Financial, patient, and appointment trends.</p>
      </div>
    </div>

    <div class="dashboard-insights-grid">
      <section class="dashboard-panel reference-dashboard-card income-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">Collections</span>
            <h2>Income Trend</h2>
            <p>Monthly payments from treatment records.</p>
          </div>
          <strong>{{
            formatMoney(incomeMonths.reduce((sum, month) => sum + month.value, 0))
          }}</strong>
        </div>
        <div class="income-chart" role="img" aria-label="Monthly clinic income chart">
          <div v-for="month in incomeMonths" :key="month.key" class="income-chart-column">
            <div class="income-chart-value" :title="`${month.label}: ${formatMoney(month.value)}`">
              <span :style="{ height: `${month.height}%` }"></span>
            </div>
            <small>{{ month.label }}</small>
          </div>
        </div>
      </section>

      <section class="dashboard-panel reference-dashboard-card status-insight-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">{{ periodLabel }}</span>
            <h2>Appointment Status</h2>
          </div>
        </div>
        <div class="analytics-bars">
          <div
            v-for="item in statusCounts"
            :key="item.status"
            class="analytics-bar-row"
            :class="item.status"
          >
            <div>
              <span>{{ item.label }}</span
              ><strong>{{ item.value }}</strong>
            </div>
            <span class="analytics-track"
              ><span :style="{ width: barWidth(statusCounts, item.value) }"></span
            ></span>
          </div>
        </div>
      </section>

      <section class="dashboard-panel reference-dashboard-card patient-insight-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">Patient care</span>
            <h2>Patient Overview</h2>
          </div>
        </div>
        <div class="analytics-bars">
          <div v-for="item in patientAnalytics" :key="item.label" class="analytics-bar-row">
            <div>
              <span>{{ item.label }}</span
              ><strong>{{ item.value }}</strong>
            </div>
            <span class="analytics-track"
              ><span :style="{ width: barWidth(patientAnalytics, item.value) }"></span
            ></span>
          </div>
        </div>
      </section>

      <section class="dashboard-panel reference-dashboard-card activity-insight-card">
        <div class="reference-card-title">
          <div>
            <span class="section-kicker">Transactions</span>
            <h2>Recent Activity</h2>
          </div>
          <span>Latest updates</span>
        </div>
        <div class="clinic-activity-feed">
          <article
            v-for="record in state.records.slice(0, 5)"
            :key="record.id"
            class="clinic-activity-item"
          >
            <span class="activity-indicator"></span>
            <div>
              <time>{{ formatDate(record.treatment_date) }}</time
              ><strong>{{ record.patient_name }} treatment updated</strong>
              <p>{{ treatmentProcedure(record) }}</p>
            </div>
          </article>
          <p v-if="!state.records.length" class="dashboard-empty">
            No clinic activity has been recorded.
          </p>
        </div>
      </section>
    </div>
  </section>
</template>
