// Enterprise AI onboarding command center UI behavior.
// Author: Sarala Biswal

const sampleProfiles = [
  {
    name: "Priya Raman",
    role: "Account Executive",
    department: "Enterprise Sales",
    startDate: "2026-06-15",
    manager: "@maria.chen",
    systems: ["laptop", "github", "google workspace", "slack", "salesforce"],
  },
  {
    name: "Mateo Alvarez",
    role: "Revenue Operations Analyst",
    department: "Growth",
    startDate: "2026-07-06",
    manager: "@samir.patel",
    systems: ["laptop", "google workspace", "slack", "salesforce"],
  },
  {
    name: "Hannah Lee",
    role: "Customer Success Manager",
    department: "Platform",
    startDate: "2026-08-03",
    manager: "@jordan.kim",
    systems: ["laptop", "github", "google workspace", "slack"],
  },
];

const sampleNames = [
  "Priya Raman",
  "Mateo Alvarez",
  "Hannah Lee",
  "Aisha Morgan",
  "Noah Bennett",
  "Lina Okafor",
  "Ethan Brooks",
  "Sofia Chen",
  "Nora Patel",
  "Julian Kim",
  "Maya Iyer",
  "Leo Martinez",
];

const sampleRoles = [
  "Account Executive",
  "Revenue Operations Analyst",
  "Customer Success Manager",
  "Sales Engineer",
  "Enablement Manager",
  "Platform Engineer",
  "Security Analyst",
  "Product Operations Manager",
];

const sampleDepartments = [
  "Enterprise Sales",
  "Growth",
  "Platform",
  "Customer Success",
  "Security",
  "Revenue Operations",
];

const sampleManagers = [
  "@maria.chen",
  "@samir.patel",
  "@jordan.kim",
  "@nora.li",
  "@elena.brooks",
  "@devon.reed",
];

const sampleSystemSets = [
  ["laptop", "github", "google workspace", "slack", "salesforce"],
  ["laptop", "google workspace", "slack", "salesforce"],
  ["laptop", "github", "google workspace", "slack"],
  ["laptop", "google workspace", "slack"],
];

const employees = [
  {
    id: "Emp-1024",
    name: "Maria Chen",
    role: "Director, Growth",
    department: "Growth",
    startDate: "2023-04-17",
    manager: "Vp revenue",
    status: "Active",
  },
  {
    id: "Emp-1188",
    name: "Samir Patel",
    role: "Security Manager",
    department: "Risk",
    startDate: "2022-10-03",
    manager: "Ciso office",
    status: "Active",
  },
  {
    id: "Emp-1261",
    name: "Jordan Kim",
    role: "Platform Lead",
    department: "Platform",
    startDate: "2021-08-12",
    manager: "Cto office",
    status: "Active",
  },
  {
    id: "Emp-1437",
    name: "Elena Brooks",
    role: "People Ops Partner",
    department: "People",
    startDate: "2024-02-05",
    manager: "Hr operations",
    status: "Active",
  },
];
const baselineEmployees = employees.map((employee) => ({ ...employee }));

const systems = [
  { key: "workday", name: "Workday", owner: "Hr agent", detail: "Employee record pending" },
  { key: "jira", name: "Jira Service", owner: "It agent", detail: "Provisioning ticket pending" },
  { key: "slack", name: "Slack", owner: "Notification Agent", detail: "Manager notice pending" },
  {
    key: "salesforce",
    name: "Salesforce",
    owner: "Salesforce Agent",
    detail: "Crm enablement record pending",
  },
];

const checklist = [
  { name: "Laptop request", detail: "Standard issue hardware profile", state: "Pending" },
  { name: "Github access", detail: "Team repository group assignment", state: "Pending" },
  { name: "Google Workspace", detail: "Mail, calendar, and drive policy", state: "Pending" },
  { name: "Slack workspace", detail: "Manager notification and team channel", state: "Pending" },
  { name: "Salesforce readiness", detail: "Crm profile and enablement tracking", state: "Pending" },
];

const controls = [
  { name: "Mcp authentication", detail: "x-mcp-api-key validated", state: "Ready" },
  { name: "Version pinning", detail: "Mcp protocol version v1", state: "Ready" },
  { name: "Sensitive data masking", detail: "Salary, ssn, token, and secret fields masked", state: "Ready" },
  { name: "Audit persistence", detail: "Sqlite write on every agent action", state: "Ready" },
];

const architectureSteps = {
  prompt:
    "The prompt moves from the browser to Fastapi, through LangChain prompt parsing, into structured employee data.",
  mode:
    "APP_MODE and per-connector settings resolve Demo Mode to mock connectors and Real Mode to sandbox cloud writes. Readiness blocks unsafe real runs before agents execute.",
  orchestration:
    "The agent orchestrator receives employee data, plans the workflow, runs specialized agents in parallel, and aggregates their results.",
  mcp:
    "Each specialized agent calls an mcp tool boundary, then writes to one target cloud: Workday, Jira, Slack, or Salesforce. Each cloud response returns an external id and URL.",
  governance:
    "Audit logging and the external records ledger turn connector responses into business evidence cards for created records.",
};

const architectureViewBoxes = {
  prompt: "0 0 860 330",
  mode: "0 0 1080 300",
  orchestration: "0 35 1080 380",
  mcp: "0 45 1160 410",
  governance: "0 45 1180 300",
};

const physicalViews = {
  poc: {
    "client-title": "Browser ui",
    "client-detail": "Static html, css, and JavaScript served by Fastapi",
    "runtime-title": "Uvicorn + Fastapi",
    "runtime-detail": "Routes, request models, orchestration, and api responses",
    "agent-title": "Agent Layer",
    "agent-detail": "Async orchestration and task execution",
    "mcp-title": "Mcp layer",
    "mcp-detail": "Auth, versioning, schemas, tool execution",
    "audit-title": "Sqlite audit.db",
    "audit-detail": "Durable local audit log for every agent action",
    "systems-title": "Mock Workday/Jira/Salesforce",
    "systems-detail": "Deterministic offline responses",
    "slack-title": "Slack api optional",
    "slack-detail": "Real call only when token and mock mode allow it",
    "metrics-title": "/metrics",
    "metrics-detail": "Prometheus-compatible operational metrics",
    "deploy-one-label": "Local",
    "deploy-one-value": "python3 -m uvicorn app.main:app --reload",
    "deploy-two-label": "Container",
    "deploy-two-value": "docker compose up --build",
    "deploy-three-label": "Ci",
    "deploy-three-value": "ruff, mypy, pytest, coverage",
  },
  production: {
    "client-title": "Enterprise Web App",
    "client-detail": "Authenticated hr portal behind sso and role-based access",
    "runtime-title": "Api gateway + Fastapi service",
    "runtime-detail": "Containerized service running behind ingress, auth, rate limits, and tracing",
    "agent-title": "Agent Workers",
    "agent-detail": "Horizontally scalable async workers for orchestration and retries",
    "mcp-title": "Mcp tool services",
    "mcp-detail": "Versioned integration services with secrets management and policy checks",
    "audit-title": "Managed Audit Store",
    "audit-detail": "Postgres, warehouse, or siem-backed immutable audit history",
    "systems-title": "Workday, Jira, Salesforce apis",
    "systems-detail": "Production api calls using service accounts and least-privilege scopes",
    "slack-title": "Slack Enterprise Grid",
    "slack-detail": "Approved bot application with enterprise channel and dm policies",
    "metrics-title": "Prometheus + Grafana",
    "metrics-detail": "Dashboards, alerts, p95 latency, error budgets, and workflow throughput",
    "deploy-one-label": "Runtime",
    "deploy-one-value": "Kubernetes or managed container platform",
    "deploy-two-label": "Security",
    "deploy-two-value": "Sso, secrets manager, api gateway, audit retention",
    "deploy-three-label": "Operations",
    "deploy-three-value": "Ci/cd, monitoring, alerts, rollback strategy",
  },
};

const $ = (id) => document.getElementById(id);

const elements = {
  activeCount: $("active-count"),
  appModePill: $("app-mode-pill"),
  apiDot: $("api-dot"),
  auditBody: $("audit-body"),
  checklist: $("checklist"),
  controlList: $("control-list"),
  currentDate: $("current-date"),
  dryRun: $("dry-run"),
  duration: $("duration"),
  employeeBody: $("employee-body"),
  extractButton: $("extract-button"),
  extractStatus: $("extract-status"),
  evidenceBoard: $("evidence-board"),
  healthText: $("health-text"),
  instruction: $("instruction"),
  lastAdded: $("last-added"),
  metricsOutput: $("metrics-output"),
  mode: $("mode"),
  newHireDepartment: $("new-hire-department"),
  newHireManager: $("new-hire-manager"),
  newHireName: $("new-hire-name"),
  newHireRole: $("new-hire-role"),
  newHireStart: $("new-hire-start"),
  openCount: $("open-count"),
  promptButton: $("prompt-button"),
  refreshAudit: $("refresh-audit"),
  runButton: $("run-button"),
  runStatus: $("run-status"),
  sampleButton: $("sample-button"),
  systemList: $("system-list"),
  timeline: $("timeline"),
  workflowId: $("workflow-id"),
};

let runtimeSettings = null;
let selectedSettingsMode = "demo";
let settingsModeTouched = false;

function nextSampleCounter() {
  const current = Number(window.localStorage.getItem("onboardingSampleCounter") || "0") + 1;
  window.localStorage.setItem("onboardingSampleCounter", String(current));
  return current;
}

function isoDateDaysFromNow(daysFromNow) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromNow);
  return date.toISOString().slice(0, 10);
}

function generatedSample() {
  const counter = nextSampleCounter();
  const profile = sampleProfiles[counter % sampleProfiles.length];
  const name = sampleNames[counter % sampleNames.length];
  const role = sampleRoles[(counter + 2) % sampleRoles.length];
  const department = sampleDepartments[(counter + 1) % sampleDepartments.length];
  const manager = sampleManagers[(counter + 3) % sampleManagers.length];
  const systems = sampleSystemSets[counter % sampleSystemSets.length];

  return {
    name,
    role: counter % 3 === 0 ? profile.role : role,
    department: counter % 4 === 0 ? profile.department : department,
    startDate: isoDateDaysFromNow(21 + counter),
    manager,
    systems,
  };
}

function getSystemInputs() {
  return [...document.querySelectorAll('input[name="systems"]')];
}

function showView(viewName) {
  const targetView = document.querySelector(`[data-view="${viewName}"]`)
    ? viewName
    : "dashboard";

  document.querySelectorAll("[data-view]").forEach((section) => {
    section.classList.toggle("active", section.dataset.view === targetView);
  });

  document.querySelectorAll("[data-view-link]").forEach((link) => {
    link.classList.toggle("active", link.dataset.viewLink === targetView);
  });
}

function showArchitectureStep(stepName) {
  const selectedStep = architectureSteps[stepName] ? stepName : "prompt";
  const caption = document.getElementById("arch-step-caption");
  if (caption) caption.textContent = architectureSteps[selectedStep];

  document.querySelectorAll("[data-arch-step]").forEach((button) => {
    button.classList.toggle("active", button.dataset.archStep === selectedStep);
  });

  const diagram = document.querySelector(".agent-diagram");
  if (diagram) {
    diagram.classList.add("is-walking");
    diagram.setAttribute("viewBox", architectureViewBoxes[selectedStep]);
  }

  document.querySelectorAll("[data-arch-node]").forEach((node) => {
    const nodeSteps = node.dataset.archNode.split(" ");
    const isActive = nodeSteps.includes(selectedStep);
    node.classList.toggle("active-step", isActive);
    node.classList.toggle("hidden-step", !isActive);
  });

  document.querySelectorAll("[data-arch-edge]").forEach((edge) => {
    const edgeSteps = edge.dataset.archEdge.split(" ");
    const isActive = edgeSteps.includes(selectedStep);
    edge.classList.toggle("active-step", isActive);
    edge.classList.toggle("hidden-step", !isActive);
  });

  document.querySelectorAll("[data-arch-label]").forEach((label) => {
    const labelSteps = label.dataset.archLabel.split(" ");
    label.classList.toggle("hidden-step", !labelSteps.includes(selectedStep));
  });
}

function showPhysicalView(viewName) {
  const selectedView = physicalViews[viewName] ? viewName : "poc";
  const content = physicalViews[selectedView];

  document.querySelectorAll("[data-physical-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.physicalView === selectedView);
  });

  document.querySelectorAll("[data-physical-content]").forEach((node) => {
    const key = node.dataset.physicalContent;
    node.textContent = content[key] || "";
  });
}

function initials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("");
}

function toTitle(value = "") {
  return value ? `${value.charAt(0).toLocaleUpperCase()}${value.slice(1)}` : "";
}

function formatLongDate(value = "") {
  if (!value) return "a date to be confirmed";
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) return value;
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function joinList(items) {
  if (items.length <= 1) return items.join("");
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items.at(-1)}`;
}

function articleFor(value = "") {
  return /^[aeiou]/i.test(value.trim()) ? "an" : "a";
}

function selectedSystems() {
  return getSystemInputs()
    .filter((input) => input.checked)
    .map((input) => input.value);
}

function normalizeSystemName(value = "") {
  const normalized = value.toLowerCase().replaceAll("_", " ").trim();
  if (["gsuite", "google", "gmail"].includes(normalized)) return "google workspace";
  if (normalized === "git hub") return "github";
  if (normalized === "crm") return "salesforce";
  return normalized;
}

function buildInstructionFromFields() {
  const name = elements.newHireName.value.trim() || "New Employee";
  const role = elements.newHireRole.value.trim() || "Employee";
  const department = elements.newHireDepartment.value.trim() || "General";
  const startDate = formatLongDate(elements.newHireStart.value);
  const manager = elements.newHireManager.value.trim() || "@manager";
  const systems = selectedSystems();
  const systemSentence = systems.length
    ? ` Required systems are ${joinList(systems)}.`
    : " Required systems will be confirmed by the manager.";

  return `Onboard ${name} as ${articleFor(role)} ${role} on the ${department} team starting ${startDate}. Manager is ${manager} on Slack.${systemSentence}`;
}

function updateInstructionPreview() {
  elements.instruction.value = buildInstructionFromFields();
}

function applySample(sample) {
  elements.newHireName.value = sample.name;
  elements.newHireRole.value = sample.role;
  elements.newHireDepartment.value = sample.department;
  elements.newHireStart.value = sample.startDate;
  elements.newHireManager.value = sample.manager;
  getSystemInputs().forEach((input) => {
    input.checked = sample.systems.includes(input.value);
  });
  updateInstructionPreview();
}

function fillFormFromExtraction(employee) {
  elements.newHireName.value = employee.full_name || "";
  elements.newHireRole.value = employee.role || "";
  elements.newHireDepartment.value = employee.department || "";
  elements.newHireStart.value = employee.start_date || "";
  elements.newHireManager.value = employee.manager_slack_handle || "";

  const systems = (employee.required_systems || []).map(normalizeSystemName);
  getSystemInputs().forEach((input) => {
    input.checked = systems.includes(normalizeSystemName(input.value));
  });
}

function formatRecordId(value = "") {
  return value.replace("EMP-", "Emp-").replace("IT-", "It-").replace("SF-", "Sf-");
}

function rosterKey(employee) {
  const id = employee.id || "";
  if (id && id.toLowerCase() !== "dry run") return `id:${id.toLowerCase()}`;
  return `person:${employee.name.toLowerCase()}|${employee.startDate}`;
}

function uniqueEmployees() {
  const seen = new Set();
  return employees.filter((employee) => {
    const key = rosterKey(employee);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function badge(text) {
  const className = text.toLowerCase().replace(/\s+/g, "-");
  return `<span class="badge ${className}">${text}</span>`;
}

function renderEmployees() {
  const roster = uniqueEmployees();
  elements.employeeBody.innerHTML = roster
    .map(
      (employee) => `<tr>
        <td>
          <div class="person-cell">
            <span class="avatar">${initials(employee.name)}</span>
            <div>
              <strong>${employee.name}</strong>
              <small>${employee.id}</small>
            </div>
          </div>
        </td>
        <td>${employee.role}</td>
        <td>${employee.department}</td>
        <td>${employee.startDate}</td>
        <td>${employee.manager}</td>
        <td>${badge(employee.status)}</td>
      </tr>`,
    )
    .join("");

  elements.activeCount.textContent = roster.filter((employee) => employee.status === "Active").length;
  elements.openCount.textContent = roster.filter((employee) =>
    ["Provisioning", "Simulated"].includes(employee.status),
  ).length;
}

function renderSystems(results = {}) {
  elements.systemList.innerHTML = systems
    .map((system) => {
      const result = results[system.key];
      const error = errorForSystem(results.errors || [], system.key);
      const state = error ? "failed" : result?.status || "pending";
      let detail = system.detail;
      if (error) detail = error;
      if (!error && system.key === "workday" && result) {
        detail = `Employee id ${formatRecordId(result.employee_id)}`;
      }
      if (system.key === "jira" && result) {
        detail = result.ticket_id ? `Ticket ${formatRecordId(result.ticket_id)}` : "Dry run only";
      }
      if (!error && system.key === "slack" && result) detail = `Manager channel ${result.channel}`;
      if (!error && system.key === "salesforce" && result) {
        detail = result.record_id ? `Crm record ${formatRecordId(result.record_id)}` : "Dry run only";
      }
      return `<div class="system-row">
        <div>
          <strong>${system.name}</strong>
          <small>${system.owner} - ${detail}</small>
        </div>
        ${badge(state)}
      </div>`;
    })
    .join("");
}

function systemLabel(system) {
  return {
    workday: "Workday employee profile",
    jira: "IT access request",
    slack: "Manager Slack notification",
    salesforce: "Salesforce readiness record",
  }[system] || toTitle(system);
}

function systemBusinessOwner(system) {
  return {
    workday: "HR operations",
    jira: "IT service desk",
    slack: "Hiring manager",
    salesforce: "Sales operations",
  }[system] || "Operations";
}

function systemBadgeLabel(system = "") {
  const normalized = normalizeEvidenceSystem(system);
  return {
    internal: "CO",
    workday: "WD",
    jira: "IT",
    slack: "SL",
    salesforce: "SF",
  }[normalized] || String(system).slice(0, 2).toLocaleUpperCase();
}

function systemBadgeClass(system = "") {
  const normalized = normalizeEvidenceSystem(system);
  return normalized === "jira" ? "internal" : normalized;
}

const evidenceSystemOrder = {
  workday: 0,
  jira: 1,
  it: 1,
  slack: 2,
  salesforce: 3,
};

function normalizeEvidenceSystem(system = "") {
  return system === "it" ? "jira" : system;
}

function sortEvidenceRecords(records = []) {
  // Evidence cards are deliberately ordered as a business process: HR profile,
  // IT access request, manager notification, then CRM readiness.
  return [...records].sort((a, b) => {
    const aSystem = normalizeEvidenceSystem(a.system);
    const bSystem = normalizeEvidenceSystem(b.system);
    const orderDelta =
      (evidenceSystemOrder[aSystem] ?? 99) - (evidenceSystemOrder[bSystem] ?? 99);
    if (orderDelta !== 0) return orderDelta;
    return String(a.external_id || "").localeCompare(String(b.external_id || ""));
  });
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function isMockRecordUrl(url = "") {
  const value = String(url).trim().toLowerCase();
  if (!value) return false;
  return (
    value.startsWith("slack://") ||
    value.includes("//mock.workday.com") ||
    value.includes("//mock.jira.com") ||
    value.includes("//mock.salesforce.com")
  );
}

function canOpenExternalRecord(record) {
  return Boolean(
    record.external_url &&
      record.mode === "real" &&
      !isMockRecordUrl(record.external_url),
  );
}

function evidenceAction(record, detailId) {
  if (canOpenExternalRecord(record)) {
    return `<a href="${escapeHtml(record.external_url)}" target="_blank" rel="noreferrer">Open external record</a>`;
  }

  return `<button class="link-button" type="button" data-evidence-toggle="${detailId}" aria-expanded="false" aria-controls="${detailId}">Open in app</button>`;
}

function evidenceDetail(record, audit, source, detailId) {
  const recorded = record.created_at ? new Date(record.created_at).toLocaleString() : "Just now";
  const storedUrl = record.external_url || "Stored in app ledger only";
  return `<div class="evidence-detail" id="${detailId}" hidden>
    <div>
      <strong>Created-record evidence</strong>
      <span>This record is stored in the app ledger and tied to the workflow audit trail.</span>
    </div>
    <dl>
      <div><dt>System</dt><dd>${escapeHtml(systemLabel(record.system))}</dd></div>
      <div><dt>Record</dt><dd>${escapeHtml(formatRecordId(record.external_id || ""))}</dd></div>
      <div><dt>Workflow</dt><dd>${escapeHtml(record.workflow_id || "Current workflow")}</dd></div>
      <div><dt>Ledger source</dt><dd>${escapeHtml(source)}</dd></div>
      <div><dt>Audit proof</dt><dd>${escapeHtml(audit ? `${audit.agent} / ${audit.tool} / ${audit.status}` : "Audit pending")}</dd></div>
      <div><dt>Recorded</dt><dd>${escapeHtml(recorded)}</dd></div>
      <div><dt>Idempotency</dt><dd>${escapeHtml(record.idempotency_key || "Workflow scoped")}</dd></div>
      <div><dt>Stored URL</dt><dd>${escapeHtml(storedUrl)}</dd></div>
    </dl>
  </div>`;
}

function evidenceRecordFromResult(workflowId, system, result) {
  if (!result) return null;
  const recordIds = {
    workday: result.employee_id,
    jira: result.ticket_id,
    slack: result.message_ts,
    salesforce: result.record_id,
  };
  const urls = {
    jira: result.url,
    salesforce: result.url,
  };
  return {
    workflow_id: workflowId,
    system,
    external_id: recordIds[system],
    external_url: urls[system] || "",
    mode: result.status === "skipped" ? "dry_run" : connectorModeForSystem(system),
    status: result.status,
    evidence_source: "Workflow response",
  };
}

function connectorModeForSystem(system) {
  const connectors = runtimeSettings?.connectors || {};
  const key = system === "jira" ? "it" : system;
  return connectors[key]?.mode || "mock";
}

function fallbackEvidenceRecords(data) {
  return [
    evidenceRecordFromResult(data.workflow_id, "workday", data.results.workday),
    evidenceRecordFromResult(data.workflow_id, "jira", data.results.jira),
    evidenceRecordFromResult(data.workflow_id, "slack", data.results.slack),
    evidenceRecordFromResult(data.workflow_id, "salesforce", data.results.salesforce),
  ].filter(Boolean);
}

function renderEvidence(records = [], auditEntries = []) {
  if (!records.length) {
    elements.evidenceBoard.innerHTML = `<div class="evidence-empty">
      <strong>No created-record evidence yet</strong>
      <span>Run a completed workflow to populate ledger-backed business evidence.</span>
    </div>`;
    return;
  }

  const auditByTool = new Map(
    auditEntries.map((entry) => [`${entry.agent}:${entry.tool}`, entry]),
  );
  const toolKeys = {
    workday: "hr_agent:create_employee",
    jira: "it_agent:create_ticket",
    slack: "notification_agent:send_message",
    salesforce: "salesforce_agent:create_onboarding_record",
  };
  const sortedRecords = sortEvidenceRecords(records);

  elements.evidenceBoard.innerHTML = `
    <div class="evidence-heading">
      <div>
        <span>Business evidence</span>
        <strong>${records.length} created artifacts</strong>
      </div>
      <small>Ledger + audit proof</small>
    </div>
    <div class="evidence-grid">
      ${sortedRecords
        .map((record, index) => {
          const audit = auditByTool.get(toolKeys[record.system]);
          const status = record.status || audit?.status || "created";
          const source = record.id ? "External ledger" : record.evidence_source || "Workflow response";
          const detailId = `evidence-detail-${index}`;
          const urlLine = evidenceAction(record, detailId);
          return `<article class="evidence-card">
            <div class="evidence-card-title">
              <span class="system-badge ${systemBadgeClass(record.system)}">
                ${systemBadgeLabel(record.system)}
              </span>
              <div>
                <strong>${systemLabel(record.system)}</strong>
                <small>${systemBusinessOwner(record.system)}</small>
              </div>
            </div>
            <dl>
              <div><dt>Record ID</dt><dd>${formatRecordId(record.external_id)}</dd></div>
              <div><dt>Status</dt><dd>${badge(status)}</dd></div>
              <div><dt>Mode</dt><dd>${badge(record.mode || "mock")}</dd></div>
              <div><dt>Proof</dt><dd>${source}</dd></div>
              <div><dt>Audit</dt><dd>${audit ? `${audit.status} / ${audit.duration_ms} ms` : "Pending"}</dd></div>
              <div><dt>Recorded</dt><dd>${record.created_at ? new Date(record.created_at).toLocaleString() : "Just now"}</dd></div>
              <div><dt>Guard</dt><dd>${record.idempotency_key || "Workflow scoped"}</dd></div>
              <div><dt>Link</dt><dd>${urlLine}</dd></div>
            </dl>
            ${evidenceDetail(record, audit, source, detailId)}
          </article>`;
        })
        .join("")}
    </div>`;
}

async function refreshEvidence(workflowId, fallbackRecords = []) {
  // Render immediately from the workflow response, then upgrade the cards with
  // ledger and audit rows when the persisted evidence endpoint responds.
  renderEvidence(fallbackRecords);
  try {
    const response = await fetch(`/workflows/${workflowId}/evidence`);
    if (!response.ok) throw new Error("Evidence unavailable");
    const evidence = await response.json();
    renderEvidence(evidence.records, evidence.audit_entries);
  } catch {
    renderEvidence(fallbackRecords);
  }
}

function renderChecklist(completed = false) {
  elements.checklist.innerHTML = checklist
    .map((item) => {
      const state = completed ? "Ready" : item.state;
      return `<div class="check-row">
        <div>
          <strong>${item.name}</strong>
          <small>${item.detail}</small>
        </div>
        ${badge(state)}
      </div>`;
    })
    .join("");
}

function renderControls() {
  elements.controlList.innerHTML = controls
    .map(
      (control) => `<div class="control-row">
        <div>
          <strong>${control.name}</strong>
          <small>${control.detail}</small>
        </div>
        ${badge(control.state)}
      </div>`,
    )
    .join("");
}

function renderEmptyTimeline() {
  elements.timeline.innerHTML = `<li class="pending">
    <span></span>
    <div class="timeline-card">
      <span class="system-badge internal">${systemBadgeLabel("internal")}</span>
      <div>
        <strong>Awaiting request</strong>
        <p>Submit a new hire to start the agent workflow.</p>
      </div>
    </div>
  </li>`;
}

function resetDashboardForModeChange() {
  // Mode changes should leave the user on the current page while removing any
  // stale workflow result that belonged to the previous execution profile.
  employees.splice(0, employees.length, ...baselineEmployees.map((employee) => ({ ...employee })));
  elements.runStatus.className = "run-status idle";
  elements.runStatus.textContent = "Ready";
  elements.workflowId.textContent = "Not run yet";
  elements.duration.textContent = "-";
  elements.mode.textContent = elements.dryRun.checked ? "Dry run" : connectorModeSummary();
  elements.lastAdded.textContent = "Source: Workday records through the external ledger";
  renderEmployees();
  renderEmptyTimeline();
  renderSystems();
  renderEvidence();
  renderChecklist(false);
}

function parseInstruction(instruction) {
  const name =
    instruction.match(/onboard\s+(.+?)\s+as\s+/i)?.[1]?.trim() || "New Employee";
  const role =
    instruction.match(/\s+as\s+(?:an|a)?\s*(.+?)\s+on\s+(?:the\s+)?/i)?.[1]?.trim() ||
    "Employee";
  const department =
    instruction.match(/\s+on\s+(?:the\s+)?(.+?)\s+team/i)?.[1]?.trim() || "General";
  const startDate =
    instruction.match(/starting\s+([A-Za-z]+\s+\d{1,2}(?:,?\s+\d{4})?|\d{4}-\d{2}-\d{2})/i)?.[1] ||
    "Tbd";
  const manager =
    instruction.match(/manager\s+is\s+(@?[A-Za-z0-9._-]+)/i)?.[1] || "@manager";
  return { name, role, department, startDate, manager };
}

function setStatus(status) {
  elements.runStatus.className = `run-status ${status}`;
  elements.runStatus.textContent = toTitle(status);
}

function errorForSystem(errors = [], systemKey) {
  const prefixes = {
    workday: "HR Agent failed:",
    jira: "IT Agent failed:",
    slack: "Notification Agent failed:",
    salesforce: "Salesforce Agent failed:",
  };
  const prefix = prefixes[systemKey];
  const error = errors.find((message) => message.startsWith(prefix));
  return error ? error.replace(prefix, "").trim() : "";
}

function timelineStateForResult(result, error) {
  if (error) return "failed";
  if (!result) return "pending";
  if (result.status === "skipped") return "warning";
  return "complete";
}

function renderTimeline(data) {
  const results = data.results;
  const errors = results.errors || [];
  const workdayError = errorForSystem(errors, "workday");
  const jiraError = errorForSystem(errors, "jira");
  const slackError = errorForSystem(errors, "slack");
  const salesforceError = errorForSystem(errors, "salesforce");
  const items = [
    {
      title: "Request understood",
      detail: "Employee data extracted and validated",
      className: "complete",
      system: "internal",
      badge: systemBadgeLabel("internal"),
    },
    {
      title: workdayError ? "Employee profile blocked" : "Employee profile created",
      detail: workdayError
        ? workdayError
        : results.workday
        ? `${results.workday.status === "existing" ? "Reused" : "Created"} Workday employee id ${formatRecordId(results.workday.employee_id)}`
        : "No Workday response",
      className: timelineStateForResult(results.workday, workdayError),
      system: "workday",
      badge: systemBadgeLabel("workday"),
    },
    {
      title: jiraError ? "Access request blocked" : "Access request opened",
      detail: jiraError
        ? jiraError
        : results.jira
        ? `${results.jira.status === "existing" ? "Reused" : "Created"} internal it ticket ${formatRecordId(results.jira.ticket_id) || "dry run"}`
        : "No Jira response",
      className: timelineStateForResult(results.jira, jiraError),
      system: "internal",
      badge: systemBadgeLabel("jira"),
    },
    {
      title: slackError ? "Manager notification blocked" : "Manager notified",
      detail: slackError
        ? slackError
        : results.slack
        ? `${results.slack.status === "existing" ? "Reused" : "Sent"} Slack message to ${results.slack.channel}`
        : "No Slack response",
      className: timelineStateForResult(results.slack, slackError),
      system: "slack",
      badge: systemBadgeLabel("slack"),
    },
    {
      title: salesforceError
        ? "Sales readiness record blocked"
        : "Sales readiness record created",
      detail: salesforceError
        ? salesforceError
        : results.salesforce
        ? `${results.salesforce.status === "existing" ? "Reused" : "Created"} Salesforce crm record ${formatRecordId(results.salesforce.record_id)}`
        : "No Salesforce response",
      className: timelineStateForResult(results.salesforce, salesforceError),
      system: "salesforce",
      badge: systemBadgeLabel("salesforce"),
    },
  ];

  elements.timeline.innerHTML = items
    .map(
      (item) => `<li class="${item.className}">
        <span></span>
        <div class="timeline-card">
          <span class="system-badge ${item.system}">${item.badge}</span>
          <div>
            <strong>${item.title}</strong>
            <p>${item.detail}</p>
          </div>
        </div>
      </li>`,
    )
    .join("");
}

function addEmployeeFromWorkflow(data) {
  const parsed = parseInstruction(elements.instruction.value);
  const workdayId = formatRecordId(data.results.workday?.employee_id) || "Dry run";
  const status = data.dry_run ? "Simulated" : "Provisioning";
  const employee = {
    id: workdayId,
    name: parsed.name,
    role: parsed.role,
    department: parsed.department,
    startDate: parsed.startDate,
    manager: parsed.manager,
    status,
  };
  const key = rosterKey(employee);
  const existingIndex = employees.findIndex((entry) => rosterKey(entry) === key);

  if (existingIndex >= 0) {
    employees[existingIndex] = { ...employees[existingIndex], ...employee };
    const [existing] = employees.splice(existingIndex, 1);
    employees.unshift(existing);
    elements.lastAdded.textContent = `${parsed.name} already exists in roster; record refreshed`;
  } else {
    employees.unshift(employee);
    elements.lastAdded.textContent = `${parsed.name} added to roster as ${status.toLowerCase()}`;
  }

  renderEmployees();
}

function renderResult(data) {
  setStatus(data.status);
  elements.workflowId.textContent = data.workflow_id;
  elements.duration.textContent = `${data.duration_ms} ms`;
  elements.mode.textContent = data.dry_run ? "Dry run" : connectorModeSummary();
  renderTimeline(data);
  renderSystems(data.results);
  refreshEvidence(data.workflow_id, fallbackEvidenceRecords(data));
  renderChecklist(data.status === "completed");
  if (data.results.workday || data.dry_run) {
    addEmployeeFromWorkflow(data);
  } else {
    elements.lastAdded.textContent =
      "No employee record was added because the workflow did not create or validate Workday";
  }
}

function renderAlreadyProcessed(status) {
  const employee = status.employee;
  const records = status.records || {};
  const workdayId = formatRecordId(records.workday?.external_id || "");
  const jiraId = formatRecordId(records.jira?.external_id || "");
  const salesforceId = formatRecordId(records.salesforce?.external_id || "");

  elements.runStatus.className = "run-status existing";
  elements.runStatus.textContent = "Already processed";
  elements.workflowId.textContent = "Workflow prevented";
  elements.duration.textContent = "-";
  elements.mode.textContent = "Existing records";
  elements.lastAdded.textContent = `${employee.full_name} already exists in Workday; workflow was not run`;
  elements.timeline.innerHTML = `<li class="warning">
    <span></span>
    <div class="timeline-card">
      <span class="system-badge workday">${systemBadgeLabel("workday")}</span>
      <div>
        <strong>Already processed</strong>
        <p>${employee.full_name} has Workday employee id ${workdayId || "on file"}.</p>
      </div>
    </div>
  </li>
  <li class="complete">
    <span></span>
    <div class="timeline-card">
      <span class="system-badge internal">${systemBadgeLabel("jira")}</span>
      <div>
        <strong>Existing downstream records</strong>
        <p>Jira ${jiraId || "record on file"}, Slack notification on file, Salesforce ${salesforceId || "record on file"}.</p>
      </div>
    </div>
  </li>`;
  const evidenceRecords = Object.entries(status.records || {}).map(([system, record]) => ({
    workflow_id: record.workflow_id || "existing",
    system: system === "it" ? "jira" : system,
    external_id: record.external_id,
    external_url: record.external_url,
    mode: record.mode,
    status: record.status,
    evidence_source: "Existing external ledger row",
  }));
  renderEvidence(evidenceRecords);
}

function renderReadinessBlocked(readiness) {
  const connectors = readiness.connectors || {};
  const blockedItems = Object.entries(connectors)
    .filter(([, details]) => details.status === "blocked")
    .map(([name, details]) => ({
      name,
      firstIssue: details.issues?.[0] || "Connector configuration is incomplete",
    }));

  setStatus("failed");
  elements.workflowId.textContent = "Pilot settings blocked";
  elements.duration.textContent = "-";
  elements.mode.textContent = "Real mode requires credentials";
  elements.lastAdded.textContent =
    "No workflow was run because real connector settings are incomplete";
  elements.timeline.innerHTML = [
    `<li class="complete">
      <span></span>
      <div class="timeline-card">
        <span class="system-badge internal">${systemBadgeLabel("internal")}</span>
        <div>
          <strong>Request understood</strong>
          <p>Employee data is ready, but real-mode settings need attention.</p>
        </div>
      </div>
    </li>`,
    ...blockedItems.map(
      (item) => `<li class="failed">
        <span></span>
        <div class="timeline-card">
          <span class="system-badge ${systemBadgeClass(item.name)}">${systemBadgeLabel(item.name)}</span>
          <div>
            <strong>${toTitle(item.name)} connector blocked</strong>
            <p>${item.firstIssue}</p>
          </div>
        </div>
      </li>`,
    ),
  ].join("");
  const errorPrefixes = {
    workday: "HR Agent failed:",
    it: "IT Agent failed:",
    slack: "Notification Agent failed:",
    salesforce: "Salesforce Agent failed:",
  };
  renderSystems({
    errors: blockedItems.map((item) => `${errorPrefixes[item.name]} ${item.firstIssue}`),
  });
  renderEvidence([]);
  renderChecklist(false);
}

function renderAudit(rows) {
  if (!rows.length) {
    elements.auditBody.innerHTML = '<tr><td colspan="4">No audit entries yet</td></tr>';
    return;
  }

  elements.auditBody.innerHTML = rows
    .slice(0, 12)
    .map((row) => {
      const created = new Date(row.created_at).toLocaleString();
      return `<tr>
        <td>${created}</td>
        <td>${row.agent}</td>
        <td>${row.tool}</td>
        <td>${badge(row.status)}</td>
      </tr>`;
    })
    .join("");
}

async function refreshAudit() {
  const response = await fetch("/audit?limit=12");
  const rows = await response.json();
  renderAudit(rows);
}

async function refreshMetrics() {
  const response = await fetch("/metrics");
  const text = await response.text();
  const metrics = parsePrometheusMetrics(text);
  renderMetrics(metrics);
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function formatMode(mode = "mock") {
  if (mode === "dry_run") return "Dry run";
  if (mode === "real") return "Real connector";
  return "Mock connector";
}

function selectedAppMode() {
  return selectedSettingsMode === "production" ? "real" : "demo";
}

function configuredModeText(connector = {}) {
  return `Configured ${connector.configured_mode || "auto"}; effective now ${formatMode(connector.mode)}`;
}

function connectorModeSummary() {
  const connectors = runtimeSettings?.connectors;
  if (!connectors) return "Mock writes";
  const modes = Object.values(connectors).map((connector) => connector.mode);
  if (modes.every((mode) => mode === "real")) return "Real connectors";
  if (modes.some((mode) => mode === "real")) return "Mixed connector modes";
  if (modes.every((mode) => mode === "dry_run")) return "Dry run";
  return "Mock writes";
}

function configuredText(configured) {
  return configured ? "Credentials configured" : "Credentials not configured";
}

function latestRecordText(record) {
  if (!record) return "No external record written yet";
  return `Last ${record.mode} record ${record.external_id}`;
}

function appModeLabel(appMode = "demo") {
  return appMode === "real" || appMode === "production" ? "Production Mode" : "Demo Mode";
}

const settingsConnectorOptions = {
  workday: {
    label: "Workday",
    demoOutcome: "Employee profile evidence",
    modeVariable: "WORKDAY_MODE",
    requiredVariables: "WORKDAY_BASE_URL, WORKDAY_TENANT, WORKDAY_ACCESS_TOKEN",
  },
  it: {
    label: "Jira",
    demoOutcome: "IT provisioning ticket evidence",
    modeVariable: "IT_MODE",
    requiredVariables: "JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN",
  },
  slack: {
    label: "Slack",
    demoOutcome: "Manager notification evidence",
    modeVariable: "SLACK_MODE",
    requiredVariables: "SLACK_BOT_TOKEN, SLACK_CHANNEL_MAP_JSON",
  },
  salesforce: {
    label: "Salesforce",
    demoOutcome: "Sales readiness record evidence",
    modeVariable: "SALESFORCE_MODE",
    requiredVariables: "SALESFORCE_INSTANCE_URL, SALESFORCE_ACCESS_TOKEN",
  },
};

function settingsConnectorRows(mode) {
  if (!runtimeSettings?.connectors) return "";
  const readiness = runtimeSettings.pilot_readiness?.connectors || {};
  return Object.entries(settingsConnectorOptions)
    .map(([key, options]) => {
      const connector = runtimeSettings.connectors[key];
      const connectorReadiness = readiness[key] || {};
      if (mode === "production") {
        const status = connectorReadiness.status || (connector.configured ? "ready" : "blocked");
        return `<article class="connector-clean-card">
          <div>
            <strong>${options.label}</strong>
            ${badge(status)}
          </div>
          <dl>
            <div><dt>Mode</dt><dd>${options.modeVariable}=real or APP_MODE=real</dd></div>
            <div><dt>Required</dt><dd>${options.requiredVariables}</dd></div>
            <div><dt>Latest</dt><dd>${escapeHtml(latestRecordText(connector.latest_record))}</dd></div>
          </dl>
        </article>`;
      }

      return `<article class="connector-clean-card">
        <div>
          <strong>${options.label}</strong>
          ${badge("mock")}
        </div>
        <dl>
          <div><dt>Mode</dt><dd>${options.modeVariable}=auto -> mock</dd></div>
          <div><dt>Creates</dt><dd>${options.demoOutcome}</dd></div>
          <div><dt>Latest</dt><dd>${escapeHtml(latestRecordText(connector.latest_record))}</dd></div>
        </dl>
      </article>`;
    })
    .join("");
}

function connectorSettingsCopy(connector, options) {
  if (selectedSettingsMode === "production") {
    return {
      mode: `Real ${options.recordLabel}`,
      modeDetail: configuredModeText(connector),
      actionLabel: "Production path",
      action: `${options.modeVariable}=real or APP_MODE=real`,
      configured: configuredText(connector.configured),
      detailLabel: "Required variables",
      detailValue: options.requiredVariables,
      latest: latestRecordText(connector.latest_record),
    };
  }

  return {
    mode: `Mock ${options.recordLabel}`,
    modeDetail: `Demo mode resolves ${options.modeVariable}=auto to mock. ${configuredModeText(connector)}`,
    actionLabel: "Demo path",
    action: `${options.modeVariable}=auto -> mock`,
    configured: "No production credentials required",
    detailLabel: "Latest evidence",
    detailValue: options.demoRecord,
    latest: latestRecordText(connector.latest_record),
  };
}

function renderConnectorSettings(prefix, connector, options) {
  const copy = connectorSettingsCopy(connector, options);
  setText(`settings-${prefix}-mode`, copy.mode);
  setText(`settings-${prefix}-mode-detail`, copy.modeDetail);
  setText(`settings-${prefix}-action-label`, copy.actionLabel);
  setText(`settings-${prefix}-action`, copy.action);
  setText(`settings-${prefix}-configured`, copy.configured);
  setText(`settings-${prefix}-detail-label`, copy.detailLabel);
  setText(`settings-${prefix}-detail-value`, copy.detailValue);
  setText(`settings-${prefix}-latest`, copy.latest);
}

function renderSettingsSnippets() {
  const title =
    selectedSettingsMode === "production" ? "Production .env settings" : "Demo .env defaults";
  const snippets =
    selectedSettingsMode === "production"
      ? [
          `APP_MODE=real
WORKDAY_MODE=auto
IT_MODE=auto
SLACK_MODE=auto
SALESFORCE_MODE=auto`,
          `WORKDAY_BASE_URL=https://...
WORKDAY_TENANT=...
WORKDAY_ACCESS_TOKEN=...
JIRA_BASE_URL=https://...`,
          `SLACK_BOT_TOKEN=xoxb-...
SALESFORCE_INSTANCE_URL=https://...
SALESFORCE_ACCESS_TOKEN=...`,
        ]
      : [
          `APP_MODE=demo
WORKDAY_MODE=auto
IT_MODE=auto
SLACK_MODE=auto
SALESFORCE_MODE=auto`,
          `LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b`,
          `DB_PATH=audit.db
MCP_API_KEY=dev-secret-key
MCP_VERSION=v1`,
        ];

  setText("settings-env-snippet-title", title);
  const grid = $("settings-env-grid");
  if (grid) grid.innerHTML = snippets.map((snippet) => `<pre>${escapeHtml(snippet)}</pre>`).join("");
}

function renderSettingsMode() {
  const isProduction = selectedSettingsMode === "production";
  const actualAppMode = runtimeSettings?.app_mode || selectedAppMode();
  const appMode = runtimeSettings ? actualAppMode : selectedAppMode();
  const isActualProduction = actualAppMode === "real";
  const profileTitle = isProduction ? "Production Mode" : "Demo Mode";
  const profileCopy = isProduction
    ? "Real connector profile for approved cloud sandboxes. Readiness and credentials are checked before production writes."
    : "Default safe profile. Workflows use mock cloud connectors, local ledger storage, and in-app evidence.";

  document.querySelectorAll("[data-settings-mode]").forEach((button) => {
    const active = button.dataset.settingsMode === selectedSettingsMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  setText(
    "settings-active-mode-label",
    `${isActualProduction ? "Production" : "Demo"} Mode active`,
  );
  setText("app-mode-pill", appModeLabel(actualAppMode));
  setText("settings-mode-title", profileTitle);
  setText("settings-mode-copy", profileCopy);
  document.querySelectorAll("[data-settings-profile]").forEach((profile) => {
    const active = profile.dataset.settingsProfile === selectedSettingsMode;
    profile.hidden = !active;
    profile.classList.toggle("active", active);
  });

  if (!runtimeSettings) {
    renderSettingsSnippets();
    return;
  }

  const connectors = runtimeSettings.connectors;
  setText("settings-env", `${toTitle(appMode)} mode / ${toTitle(runtimeSettings.environment)}`);
  setText(
    "settings-env-detail",
    isProduction
      ? "Saved as APP_MODE=real for this running app"
      : "Saved as APP_MODE=demo for this running app",
  );
  setText(
    "settings-workflow-mode",
    isProduction ? "Production connector writes" : "Demo connector writes",
  );
  setText(
    "settings-workflow-detail",
    isProduction
      ? "Auto connector modes resolve to real and require readiness checks"
      : "Auto connector modes resolve to mock and never call vendor APIs",
  );
  setText(
    "settings-pilot-readiness",
    isProduction ? toTitle(runtimeSettings.pilot_readiness.status) : "Not required",
  );
  setText(
    "settings-readiness-detail",
    isProduction
      ? "Resolve blocked connector credentials before production runs"
      : "Production credentials are not required for demo mode",
  );
  setText("settings-audit-store", runtimeSettings.database);
  setText("settings-mcp-version", runtimeSettings.mcp_version);
  setText("settings-production-status", toTitle(runtimeSettings.pilot_readiness.status));

  renderConnectorSettings("workday", connectors.workday, {
    modeVariable: "WORKDAY_MODE",
    recordLabel: "Workday records",
    demoRecord: "Worker profile evidence",
    requiredVariables: "WORKDAY_BASE_URL, WORKDAY_TENANT, WORKDAY_ACCESS_TOKEN",
  });
  renderConnectorSettings("jira", connectors.it, {
    modeVariable: "IT_MODE",
    recordLabel: "Jira tickets",
    demoRecord: "Provisioning ticket evidence",
    requiredVariables: "JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN",
  });
  renderConnectorSettings("slack", connectors.slack, {
    modeVariable: "SLACK_MODE",
    recordLabel: "Slack messages",
    demoRecord: "Manager notification evidence",
    requiredVariables: "SLACK_BOT_TOKEN, SLACK_CHANNEL_MAP_JSON",
  });
  renderConnectorSettings("salesforce", connectors.salesforce, {
    modeVariable: "SALESFORCE_MODE",
    recordLabel: "Salesforce records",
    demoRecord: connectors.salesforce.readiness_object,
    requiredVariables: "SALESFORCE_INSTANCE_URL, SALESFORCE_ACCESS_TOKEN",
  });

  const demoGrid = $("settings-demo-connectors");
  if (demoGrid) demoGrid.innerHTML = settingsConnectorRows("demo");
  const productionGrid = $("settings-production-connectors");
  if (productionGrid) productionGrid.innerHTML = settingsConnectorRows("production");

  renderSettingsSnippets();
}

async function refreshSettings() {
  try {
    const response = await fetch("/settings");
    if (!response.ok) throw new Error("Settings unavailable");
    runtimeSettings = await response.json();
    if (!settingsModeTouched) {
      selectedSettingsMode = runtimeSettings.app_mode === "real" ? "production" : "demo";
    }

    setText("settings-llm-provider", toTitle(runtimeSettings.llm.provider));
    setText("settings-ollama-model", runtimeSettings.llm.ollama_model);
    setText(
      "settings-cloud-options",
      `Openai ${runtimeSettings.llm.openai_model} or Anthropic ${runtimeSettings.llm.anthropic_model}`,
    );
    renderSettingsMode();
  } catch {
    runtimeSettings = null;
    renderSettingsMode();
  }
}

async function setSettingsMode(mode) {
  selectedSettingsMode = mode === "production" ? "production" : "demo";
  settingsModeTouched = true;
  renderSettingsMode();

  try {
    const response = await fetch("/settings/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: selectedSettingsMode }),
    });
    if (!response.ok) throw new Error("Mode update failed");
    runtimeSettings = await response.json();
    selectedSettingsMode = runtimeSettings.app_mode === "real" ? "production" : "demo";
    renderSettingsMode();
    resetDashboardForModeChange();
    elements.mode.textContent = elements.dryRun.checked ? "Dry run" : connectorModeSummary();
  } catch (error) {
    setText("settings-mode-copy", error.message);
    await refreshSettings();
  }
}

function parsePrometheusMetrics(text) {
  const workflows = {};
  const agentCalls = [];
  let durationCount = 0;
  let durationSum = 0;

  text.split("\n").forEach((line) => {
    if (!line || line.startsWith("#") || line.includes("_created")) return;

    const metricMatch = line.match(/^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{([^}]*)\})?\s+(.+)$/);
    if (!metricMatch) return;

    const [, name, , labelText = "", rawValue] = metricMatch;
    const value = Number(rawValue);
    const labels = Object.fromEntries(
      labelText
        .split(",")
        .filter(Boolean)
        .map((pair) => {
          const [key, rawLabelValue] = pair.split("=");
          return [key, rawLabelValue.replaceAll('"', "")];
        }),
    );

    if (name === "onboarding_workflows_total") {
      workflows[labels.status || "unknown"] = value;
    }

    if (name === "agent_calls_total") {
      agentCalls.push({
        agent: labels.agent,
        tool: labels.tool,
        status: labels.status,
        mode: labels.mode || "unknown",
        count: value,
      });
    }

    if (name === "onboarding_workflow_duration_ms_count") {
      durationCount = value;
    }

    if (name === "onboarding_workflow_duration_ms_sum") {
      durationSum = value;
    }
  });

  return {
    workflows,
    agentCalls,
    durationCount,
    durationSum,
  };
}

function renderMetrics(metrics) {
  const completed = metrics.workflows.completed || 0;
  const partial = metrics.workflows.partial || 0;
  const failed = metrics.workflows.failed || 0;
  const total = completed + partial + failed;
  const successfulAgentCalls = metrics.agentCalls
    .filter((call) => call.status === "success")
    .reduce((sum, call) => sum + call.count, 0);
  const skippedAgentCalls = metrics.agentCalls
    .filter((call) => call.status === "skipped")
    .reduce((sum, call) => sum + call.count, 0);
  const averageLatency = metrics.durationCount
    ? Math.round(metrics.durationSum / metrics.durationCount)
    : 0;

  if (!total && !metrics.agentCalls.length) {
    elements.metricsOutput.innerHTML =
      '<div class="empty-state">No workflow metrics emitted yet. Run onboarding once to populate this view.</div>';
    return;
  }

  const agentRows = metrics.agentCalls
    .sort((a, b) => `${a.agent}${a.status}${a.mode}`.localeCompare(`${b.agent}${b.status}${b.mode}`))
    .map(
      (call) => `<tr>
        <td>${formatAgentName(call.agent)}</td>
        <td>${formatToolName(call.tool)}</td>
        <td>${badge(call.status)} ${badge(call.mode)}</td>
        <td>${call.count}</td>
      </tr>`,
    )
    .join("");

  elements.metricsOutput.innerHTML = `
    <div class="metric-summary">
      <div class="metric-tile">
        <span>Workflows Run</span>
        <strong>${total}</strong>
        <small>${completed} completed, ${partial} partial, ${failed} failed</small>
      </div>
      <div class="metric-tile">
        <span>Agent Actions</span>
        <strong>${successfulAgentCalls + skippedAgentCalls}</strong>
        <small>${successfulAgentCalls} writes, ${skippedAgentCalls} dry-run validations</small>
      </div>
      <div class="metric-tile">
        <span>Avg Duration</span>
        <strong>${averageLatency} ms</strong>
        <small>Target is under 10 seconds</small>
      </div>
    </div>
    <div class="metric-table table-wrap">
      <table>
        <thead>
          <tr>
            <th>Agent</th>
            <th>Tool</th>
            <th>Status</th>
            <th>Calls</th>
          </tr>
        </thead>
        <tbody>${agentRows}</tbody>
      </table>
    </div>
    <div class="metric-note">
      This panel translates Prometheus counters into demo-friendly operations metrics.
      The raw machine-readable stream is still available at /metrics for Prometheus or Grafana.
    </div>`;
}

function formatAgentName(agent = "") {
  return agent
    .replace("_agent", "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toLocaleUpperCase());
}

function formatToolName(tool = "") {
  return tool.replaceAll("_", " ");
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Api unavailable");
    elements.apiDot.classList.add("ok");
    elements.healthText.textContent = "Api online";
  } catch {
    elements.apiDot.classList.remove("ok");
    elements.healthText.textContent = "Api offline";
  }
}

async function runWorkflow() {
  elements.runButton.disabled = true;
  elements.runButton.textContent = "Checking";
  setStatus("idle");

  try {
    if (!elements.dryRun.checked) {
      if (!runtimeSettings) await refreshSettings();
      if (runtimeSettings?.pilot_readiness?.status === "blocked") {
        renderReadinessBlocked(runtimeSettings.pilot_readiness);
        return;
      }

      const statusResponse = await fetch("/onboard/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instruction: elements.instruction.value,
          dry_run: false,
        }),
      });
      const status = await statusResponse.json();
      if (!statusResponse.ok) throw new Error(status.detail || "Status check failed");
      if (status.processed) {
        renderAlreadyProcessed(status);
        return;
      }
    }

    elements.runButton.textContent = "Running";
    const response = await fetch("/onboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        instruction: elements.instruction.value,
        dry_run: elements.dryRun.checked,
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Workflow failed");

    renderResult(data);
    await Promise.all([refreshAudit(), refreshMetrics()]);
  } catch (error) {
    setStatus("failed");
    elements.workflowId.textContent = "Request failed";
    elements.timeline.innerHTML = `<li class="warning">
      <span></span>
      <div>
        <strong>Workflow failed</strong>
        <p>${error.message}</p>
      </div>
    </li>`;
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.textContent = "Run workflow";
  }
}

async function extractFieldsFromPrompt() {
  elements.extractButton.disabled = true;
  elements.extractButton.textContent = "Extracting";
  elements.extractStatus.textContent = "Reading prompt";

  try {
    const response = await fetch("/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        instruction: elements.instruction.value,
        dry_run: true,
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Extraction failed");

    fillFormFromExtraction(data);
    updateInstructionPreview();
    elements.extractStatus.textContent = "Fields updated";
  } catch (error) {
    elements.extractStatus.textContent = error.message;
  } finally {
    elements.extractButton.disabled = false;
    elements.extractButton.textContent = "Generate form (extract fields)";
  }
}

elements.currentDate.textContent = new Date().toLocaleDateString(undefined, {
  month: "short",
  day: "numeric",
  year: "numeric",
});

elements.runButton.addEventListener("click", runWorkflow);
elements.extractButton.addEventListener("click", extractFieldsFromPrompt);
elements.promptButton.addEventListener("click", updateInstructionPreview);
elements.sampleButton.addEventListener("click", () => {
  applySample(generatedSample());
});
[
  elements.newHireDepartment,
  elements.newHireManager,
  elements.newHireName,
  elements.newHireRole,
  elements.newHireStart,
  ...getSystemInputs(),
].forEach((input) => {
  input.addEventListener("input", updateInstructionPreview);
  input.addEventListener("change", updateInstructionPreview);
});
elements.refreshAudit.addEventListener("click", refreshAudit);
elements.dryRun.addEventListener("change", () => {
  elements.mode.textContent = elements.dryRun.checked ? "Dry run" : connectorModeSummary();
});
document.querySelectorAll("[data-view-link]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const viewName = link.dataset.viewLink;
    history.replaceState(null, "", `#${viewName}`);
    showView(viewName);
  });
});
document.querySelectorAll("[data-arch-step]").forEach((button) => {
  button.addEventListener("click", () => showArchitectureStep(button.dataset.archStep));
});
document.querySelectorAll("[data-physical-view]").forEach((button) => {
  button.addEventListener("click", () => showPhysicalView(button.dataset.physicalView));
});
document.querySelectorAll("[data-settings-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    setSettingsMode(button.dataset.settingsMode || "demo");
  });
});
elements.evidenceBoard.addEventListener("click", (event) => {
  const button = event.target.closest("[data-evidence-toggle]");
  if (!button) return;

  const detail = document.getElementById(button.dataset.evidenceToggle);
  if (!detail) return;

  const isOpening = detail.hidden;
  detail.hidden = !isOpening;
  button.setAttribute("aria-expanded", String(isOpening));
  button.textContent = isOpening ? "Hide evidence" : "Open in app";
});

renderEmployees();
renderSystems();
renderEvidence();
renderChecklist();
renderControls();
renderSettingsMode();
applySample(generatedSample());
checkHealth();
refreshAudit();
refreshMetrics();
refreshSettings();
showView(window.location.hash.replace("#", "") || "dashboard");
showArchitectureStep("prompt");
showPhysicalView("poc");
