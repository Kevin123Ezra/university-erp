import { useEffect, useMemo, useState } from "react";

const pageMeta = [
  { id: "overview", label: "Overview" },
  { id: "students", label: "Students" },
  { id: "faculty", label: "Faculty" },
  { id: "courses", label: "Courses" },
  { id: "study_assistant", label: "Study Assistant" },
  { id: "timetable", label: "Timetable" },
  { id: "assignments", label: "Assignments" },
  { id: "submissions", label: "Submissions" },
  { id: "exams", label: "Exams" },
  { id: "results", label: "Results" },
  { id: "resits", label: "Resits" },
  { id: "fees", label: "Fees" },
  { id: "scholarships", label: "Scholarships" },
  { id: "library", label: "Library" },
  { id: "issues", label: "Issues" },
];

const roleTitles = {
  student: "Student workspace",
  faculty: "Faculty workspace",
  admin: "Admin operations",
};

const rolePages = {
  student: ["overview", "courses", "study_assistant", "timetable", "assignments", "exams", "results", "resits", "fees", "scholarships", "library"],
  faculty: ["overview", "students", "timetable", "assignments", "submissions", "exams", "results", "issues"],
  admin: pageMeta.map((page) => page.id),
};

async function odooJsonRpc(url, params = {}) {
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", method: "call", params, id: Date.now() }),
  });
  if (!response.ok) throw new Error(`Request failed with ${response.status}`);
  const payload = await response.json();
  if (payload.error) throw new Error(payload.error.data?.message || payload.error.message || "Odoo RPC error");
  return payload.result;
}

const loadDatabases = () => odooJsonRpc("/web/database/list");
const authenticate = ({ db, login, password }) => odooJsonRpc("/web/session/authenticate", { db, login, password });
const getSessionInfo = () => odooJsonRpc("/web/session/get_session_info");
const fetchPortalData = () => odooJsonRpc("/uni/api/portal_data");
const logout = () => odooJsonRpc("/web/session/destroy");
const createStudent = (values) => odooJsonRpc("/uni/api/students/create", { values });
const createFaculty = (values) => odooJsonRpc("/uni/api/faculty/create", { values });
const createCourse = (values) => odooJsonRpc("/uni/api/courses/create", { values });
const updateCourse = (course_id, values) => odooJsonRpc("/uni/api/courses/update", { course_id, values });
const createRegistration = (values) => odooJsonRpc("/uni/api/registrations/create", { values });
const createAssignment = (values) => odooJsonRpc("/uni/api/assignments/create", { values });
const updateAssignment = (assignment_id, values) => odooJsonRpc("/uni/api/assignments/update", { assignment_id, values });
const publishAssignment = (assignment_id) => odooJsonRpc("/uni/api/assignments/publish", { assignment_id });
const deleteAssignment = (assignment_id) => odooJsonRpc("/uni/api/assignments/delete", { assignment_id });
const createSubmission = (values) => odooJsonRpc("/uni/api/submissions/create", { values });
const gradeSubmission = (submission_id, score, feedback) => odooJsonRpc("/uni/api/submissions/grade", { submission_id, score, feedback });
const createExam = (values) => odooJsonRpc("/uni/api/exams/create", { values });
const updateExam = (exam_id, values) => odooJsonRpc("/uni/api/exams/update", { exam_id, values });
const publishExam = (exam_id) => odooJsonRpc("/uni/api/exams/publish", { exam_id });
const deleteExam = (exam_id) => odooJsonRpc("/uni/api/exams/delete", { exam_id });
const submitExam = (exam_id, answers) => odooJsonRpc("/uni/api/exams/submit", { exam_id, answers });
const gradeWrittenExam = (result_id, grades, note) => odooJsonRpc("/uni/api/exam_results/grade_written", { result_id, grades, note });
const createResit = (values) => odooJsonRpc("/uni/api/resits/create", { values });
const payFee = (invoice_id, amount) => odooJsonRpc("/uni/api/fees/pay", { invoice_id, amount });
const requestStudyAssistant = (notes, course_id, file_name, file_data) => odooJsonRpc("/uni/api/ai/study_assistant", { notes, course_id, file_name, file_data });
const requestFeedbackDraft = (assignment_title, student_name, score, short_note) =>
  odooJsonRpc("/uni/api/ai/feedback_draft", { assignment_title, student_name, score, short_note });
const triggerRiskScan = () => odooJsonRpc("/uni/api/ai/risk_scan");
const updateLibraryLoan = (loan_id, state, fine_amount) => odooJsonRpc("/uni/api/library_loans/update", { loan_id, state, fine_amount });

function formatValue(value) {
  if (Array.isArray(value)) return value[1];
  if (value === false || value === null || value === undefined || value === "") return "-";
  return String(value);
}

function normalizeRiskLevel(value) {
  const risk = String(value || "").toLowerCase();
  return ["low", "medium", "high", "critical"].includes(risk) ? risk : "";
}

function renderCellValue(column, value) {
  if (column === "risk_level") {
    const risk = normalizeRiskLevel(value);
    if (risk) {
      return <span className={`inlineBadge riskBadge ${risk}`}>{formatValue(value)}</span>;
    }
  }
  return formatValue(value);
}

function getAcronym(name) {
  return String(name || "")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 3)
    .toUpperCase() || "VMU";
}

function buildOptions(records, labelKeys) {
  return (records || []).map((record) => ({
    value: String(record.id),
    label: labelKeys.map((key) => formatValue(record[key])).join(" | "),
  }));
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = typeof reader.result === "string" ? reader.result.split(",").pop() : "";
      resolve(result || "");
    };
    reader.onerror = () => reject(new Error("Failed to read file."));
    reader.readAsDataURL(file);
  });
}

function dataHrefFromBase64(base64) {
  return `data:application/octet-stream;base64,${base64}`;
}

function buildStudentAlerts(pages) {
  const alerts = [];
  (pages.notifications || []).forEach((record) => {
    alerts.push({ id: `note-${record.id}`, title: record.name, body: record.message, createdAt: record.schedule_date || "" });
  });
  (pages.assignments || []).forEach((assignment) => {
    alerts.push({ id: `assignment-${assignment.id}`, title: "New assignment posted", body: `${assignment.name} was posted for ${formatValue(assignment.course_id)}.`, createdAt: assignment.due_date || "" });
  });
  (pages.submissions || []).filter((submission) => submission.state === "graded").forEach((submission) => {
    alerts.push({ id: `graded-${submission.id}`, title: "Assignment graded", body: `${formatValue(submission.assignment_id)} has been graded.`, createdAt: submission.submission_date || "" });
  });
  return alerts.sort((left, right) => String(right.createdAt || "").localeCompare(String(left.createdAt || "")));
}

function NotificationDrawer({ open, onClose, notifications }) {
  return (
    <>
      {open ? <div className="drawerBackdrop" onClick={onClose} /> : null}
      <aside className={open ? "notificationDrawer open" : "notificationDrawer"}>
        <div className="drawerHeader">
          <div>
            <p className="eyebrow">Student alerts</p>
            <h2>Notifications</h2>
          </div>
          <button type="button" className="ghostButton" onClick={onClose}>Close</button>
        </div>
        <div className="drawerBody">
          {notifications.length ? notifications.map((notification) => (
            <article key={notification.id} className="drawerCard">
              <strong>{notification.title}</strong>
              <p>{notification.body}</p>
            </article>
          )) : <p className="muted">No notifications right now.</p>}
        </div>
      </aside>
    </>
  );
}

function SectionHeader({ title }) {
  return (
    <section className="sectionHeader">
      <div>
        <p className="eyebrow">Visionary Minds University</p>
        <h1>{title}</h1>
      </div>
    </section>
  );
}

function OverviewPage({ dashboard }) {
  return (
    <>
      <section className="heroPanel">
        <div>
          <p className="eyebrow">{roleTitles[dashboard.role] || "Visionary Minds University"}</p>
          <h1>{dashboard.university_name}</h1>
          <p className="tagline">{dashboard.tagline}</p>
        </div>
        <div className="badge">{dashboard.role}</div>
      </section>
      <section className="metricGrid">
        {dashboard.cards.map((card) => (
          <article key={card.label} className="card metricCard">
            <span className="label">{card.label}</span>
            <strong>{card.value}</strong>
            <p>{card.hint}</p>
          </article>
        ))}
      </section>
    </>
  );
}

function FacultyOverview({ dashboard, pages }) {
  const todayKey = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"][new Date().getDay()];
  const todaysClasses = (pages.timetable || []).filter((slot) => String(slot.weekday || "").slice(0, 3).toLowerCase() === todayKey);
  return (
    <>
      <OverviewPage dashboard={dashboard} />
      <section className="contentGrid">
        <article className="card dataCard">
          <h2>My subjects</h2>
          {pages.courses?.length ? (
            <div className="stackList">
              {pages.courses.map((course) => (
                <div key={course.id} className="listCard">
                  <strong>{formatValue(course.code)} | {formatValue(course.name)}</strong>
                  <p>{formatValue(course.term_id)} | {formatValue(course.credit_hours)} credit hours</p>
                </div>
              ))}
            </div>
          ) : <p className="muted">No teaching subjects assigned yet.</p>}
        </article>
        <article className="card dataCard">
          <h2>Today's classes</h2>
          {todaysClasses.length ? (
            <div className="stackList">
              {todaysClasses.map((slot) => (
                <div key={slot.id} className="listCard">
                  <strong>{formatValue(slot.course_id)}</strong>
                  <p>{formatValue(slot.weekday)} | {formatValue(slot.start_hour)} - {formatValue(slot.end_hour)} | {formatValue(slot.room)}</p>
                </div>
              ))}
            </div>
          ) : <p className="muted">No classes scheduled for today.</p>}
        </article>
      </section>
    </>
  );
}

function TimetableWeekView({ title, records, emptyMessage = "No classes scheduled yet." }) {
  const days = [
    { key: "mon", label: "Mon" },
    { key: "tue", label: "Tue" },
    { key: "wed", label: "Wed" },
    { key: "thu", label: "Thu" },
    { key: "fri", label: "Fri" },
    { key: "sat", label: "Sat" },
    { key: "sun", label: "Sun" },
  ];
  const normalizedRecords = (records || []).map((record) => ({
    ...record,
    dayKey: String(record.weekday || "").slice(0, 3).toLowerCase(),
  }));
  const slotsByDay = Object.fromEntries(days.map((day) => [day.key, normalizedRecords.filter((record) => record.dayKey === day.key).sort((left, right) => Number(left.start_hour || 0) - Number(right.start_hour || 0))]));
  const hasAny = days.some((day) => slotsByDay[day.key]?.length);
  return (
    <section className="card dataCard">
      <h2>{title}</h2>
      {hasAny ? (
        <div className="weekGrid">
          {days.map((day) => (
            <div key={day.key} className="weekColumn">
              <div className="weekHeading">{day.label}</div>
              <div className="weekColumnBody">
                {slotsByDay[day.key]?.length ? slotsByDay[day.key].map((slot) => (
                  <article key={slot.id} className="weekEvent">
                    <strong>{formatValue(slot.course_id)}</strong>
                    <p>{formatValue(slot.start_hour)} - {formatValue(slot.end_hour)}</p>
                    <p>{formatValue(slot.room)}</p>
                    <p className="muted">{formatValue(slot.faculty_id)}</p>
                  </article>
                )) : <p className="muted">No class</p>}
              </div>
            </div>
          ))}
        </div>
      ) : <p className="muted">{emptyMessage}</p>}
    </section>
  );
}

function DataTable({ title, records, actions, hiddenColumns = [] }) {
  if (!records?.length) {
    return <section className="card dataCard"><h2>{title}</h2><p className="muted">No records available yet.</p></section>;
  }
  const columns = Object.keys(records[0]).filter((column) => column !== "file_data" && !hiddenColumns.includes(column));
  return (
    <section className="card dataCard">
      <h2>{title}</h2>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => <th key={column}>{column}</th>)}
              {actions ? <th>actions</th> : null}
            </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id}>
                  {columns.map((column) => <td key={column}>{renderCellValue(column, record[column])}</td>)}
                  {actions ? <td>{actions(record)}</td> : null}
                </tr>
              ))}
            </tbody>
        </table>
      </div>
    </section>
  );
}

function SectionMessage({ message }) {
  if (!message) return null;
  return <section className="card dataCard"><p className="muted actionMessage">{message}</p></section>;
}

function SimpleForm({ title, fields, onSubmit, submitLabel, busy, message }) {
  const initial = useMemo(() => Object.fromEntries(fields.map((field) => [field.name, field.defaultValue || ""])), [fields]);
  const [form, setForm] = useState(initial);
  const [formKey, setFormKey] = useState(0);

  useEffect(() => {
    setForm(initial);
  }, [initial, title]);

  return (
    <section className="card dataCard formCard">
      <h2>{title}</h2>
      <form
        className="inlineForm"
        onSubmit={async (event) => {
          event.preventDefault();
          await onSubmit(form, () => {
            setForm(initial);
            setFormKey((value) => value + 1);
          });
        }}
      >
        {fields.map((field) => (
          <label key={field.name}>
            <span>{field.label}</span>
            {field.type === "textarea" ? (
              <textarea value={form[field.name]} onChange={(event) => setForm((current) => ({ ...current, [field.name]: event.target.value }))} required={field.required} />
            ) : field.type === "select" ? (
              <select value={form[field.name]} onChange={(event) => setForm((current) => ({ ...current, [field.name]: event.target.value }))} required={field.required}>
                <option value="">Select</option>
                {field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            ) : field.type === "file" ? (
              <input key={`${field.name}-${formKey}`} type="file" accept={field.accept} required={field.required} onChange={(event) => setForm((current) => ({ ...current, [field.name]: event.target.files?.[0] || null }))} />
            ) : (
              <input type={field.type || "text"} value={form[field.name]} onChange={(event) => setForm((current) => ({ ...current, [field.name]: event.target.value }))} required={field.required} />
            )}
          </label>
        ))}
        <button className="primaryButton compactButton" type="submit" disabled={busy}>{busy ? "Saving..." : submitLabel}</button>
      </form>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function QuestionBuilder({ questions, setQuestions, questionTypes, defaultType = "text", title = "Questions" }) {
  const [draft, setDraft] = useState({
    question_text: "",
    question_type: defaultType,
    marks: "1",
    option_a: "",
    option_b: "",
    option_c: "",
    option_d: "",
    correct_option: "a",
  });

  function addQuestion() {
    if (!draft.question_text) return;
    if (draft.question_type === "mcq" && (!draft.option_a || !draft.option_b || !draft.option_c || !draft.option_d)) return;
    setQuestions((current) => [...current, { ...draft, marks: Number(draft.marks || 1) }]);
    setDraft({ question_text: "", question_type: defaultType, marks: "1", option_a: "", option_b: "", option_c: "", option_d: "", correct_option: "a" });
  }

  return (
    <section className="card dataCard formCard">
      <h2>{title}</h2>
      <div className="questionList">
        {questions.map((question, index) => (
          <div key={`${question.question_text}-${index}`} className="listCard">
            <strong>{index + 1}. {question.question_text}</strong>
            <p>{question.question_type} | {question.marks} marks</p>
            {question.question_type === "mcq" ? <p>{question.option_a} / {question.option_b} / {question.option_c} / {question.option_d}</p> : null}
            <button type="button" className="ghostButton inlineActionButton" onClick={() => setQuestions((current) => current.filter((_, currentIndex) => currentIndex !== index))}>Remove</button>
          </div>
        ))}
      </div>
      <div className="inlineForm">
        <label>
          <span>Question type</span>
          <select value={draft.question_type} onChange={(event) => setDraft((current) => ({ ...current, question_type: event.target.value }))}>
            {questionTypes.map((questionType) => <option key={questionType.value} value={questionType.value}>{questionType.label}</option>)}
          </select>
        </label>
        <label><span>Question</span><textarea value={draft.question_text} onChange={(event) => setDraft((current) => ({ ...current, question_text: event.target.value }))} /></label>
        <label><span>Marks</span><input type="number" value={draft.marks} onChange={(event) => setDraft((current) => ({ ...current, marks: event.target.value }))} /></label>
        {draft.question_type === "mcq" ? (
          <>
            <label><span>Option A</span><input type="text" value={draft.option_a} onChange={(event) => setDraft((current) => ({ ...current, option_a: event.target.value }))} /></label>
            <label><span>Option B</span><input type="text" value={draft.option_b} onChange={(event) => setDraft((current) => ({ ...current, option_b: event.target.value }))} /></label>
            <label><span>Option C</span><input type="text" value={draft.option_c} onChange={(event) => setDraft((current) => ({ ...current, option_c: event.target.value }))} /></label>
            <label><span>Option D</span><input type="text" value={draft.option_d} onChange={(event) => setDraft((current) => ({ ...current, option_d: event.target.value }))} /></label>
            <label>
              <span>Correct option</span>
              <select value={draft.correct_option} onChange={(event) => setDraft((current) => ({ ...current, correct_option: event.target.value }))}>
                <option value="a">A</option>
                <option value="b">B</option>
                <option value="c">C</option>
                <option value="d">D</option>
              </select>
            </label>
          </>
        ) : null}
      </div>
      <button type="button" className="ghostButton compactButton" onClick={addQuestion}>Add question</button>
    </section>
  );
}

function AssignmentCreationPanel({ busy, message, courseOptions, termOptions, onCreate, panelTitle = "Create assignment", submitLabel = "Create assignment", initialForm, initialQuestions = [], initialKey = "new-assignment" }) {
  const emptyForm = { name: "", course_id: "", term_id: "", due_date: "", total_marks: "100", instructions: "", assignment_type: "upload", instruction_file: null, instruction_file_name: "", instruction_file_data: false };
  const [form, setForm] = useState(initialForm || emptyForm);
  const [questions, setQuestions] = useState(initialQuestions);
  useEffect(() => {
    setForm(initialForm || emptyForm);
    setQuestions(initialQuestions);
  }, [initialKey]);
  return (
    <>
      <section className="card dataCard formCard">
        <h2>{panelTitle}</h2>
        <form className="inlineForm" onSubmit={async (event) => {
          event.preventDefault();
          await onCreate(form, questions, () => {
            setForm(emptyForm);
            setQuestions([]);
          });
        }}>
          <label><span>Title</span><input type="text" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required /></label>
          <label><span>Course</span><select value={form.course_id} onChange={(event) => setForm((current) => ({ ...current, course_id: event.target.value }))} required><option value="">Select</option>{courseOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>Term</span><select value={form.term_id} onChange={(event) => setForm((current) => ({ ...current, term_id: event.target.value }))} required><option value="">Select</option>{termOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>Due date</span><input type="date" value={form.due_date} onChange={(event) => setForm((current) => ({ ...current, due_date: event.target.value }))} required /></label>
          <label><span>Total marks</span><input type="number" value={form.total_marks} onChange={(event) => setForm((current) => ({ ...current, total_marks: event.target.value }))} required /></label>
          <label><span>Assignment type</span><select value={form.assignment_type} onChange={(event) => setForm((current) => ({ ...current, assignment_type: event.target.value }))}><option value="upload">Upload document</option><option value="quiz">MCQ quiz</option></select></label>
          <label><span>Instructions</span><textarea value={form.instructions} onChange={(event) => setForm((current) => ({ ...current, instructions: event.target.value }))} /></label>
          {form.instruction_file_name && !form.instruction_file ? <p className="muted">Current instruction file: {form.instruction_file_name}</p> : null}
          {form.assignment_type === "upload" ? <label><span>Instruction file</span><input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(event) => setForm((current) => ({ ...current, instruction_file: event.target.files?.[0] || null }))} /></label> : null}
          <button className="primaryButton compactButton" type="submit" disabled={busy}>{busy ? "Saving..." : submitLabel}</button>
        </form>
        {message ? <p className="muted actionMessage">{message}</p> : null}
      </section>
      {form.assignment_type === "quiz" ? <QuestionBuilder questions={questions} setQuestions={setQuestions} questionTypes={[{ value: "mcq", label: "MCQ" }]} defaultType="mcq" title="Quiz questions" /> : null}
    </>
  );
}

function ExamCreationPanel({ busy, message, courseOptions, termOptions, onCreate, panelTitle = "Create online exam", submitLabel = "Create exam", initialForm, initialQuestions = [], initialKey = "new-exam" }) {
  const emptyForm = { name: "", course_id: "", term_id: "", exam_date: "", start_hour: "10", end_hour: "12", room: "Online", capacity: "200" };
  const [form, setForm] = useState(initialForm || emptyForm);
  const [questions, setQuestions] = useState(initialQuestions);
  useEffect(() => {
    setForm(initialForm || emptyForm);
    setQuestions(initialQuestions);
  }, [initialKey]);
  return (
    <>
      <section className="card dataCard formCard">
        <h2>{panelTitle}</h2>
        <form className="inlineForm" onSubmit={async (event) => {
          event.preventDefault();
          await onCreate(form, questions, () => {
            setForm(emptyForm);
            setQuestions([]);
          });
        }}>
          <label><span>Exam name</span><input type="text" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required /></label>
          <label><span>Course</span><select value={form.course_id} onChange={(event) => setForm((current) => ({ ...current, course_id: event.target.value }))} required><option value="">Select</option>{courseOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>Term</span><select value={form.term_id} onChange={(event) => setForm((current) => ({ ...current, term_id: event.target.value }))} required><option value="">Select</option>{termOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>Exam date</span><input type="date" value={form.exam_date} onChange={(event) => setForm((current) => ({ ...current, exam_date: event.target.value }))} required /></label>
          <label><span>Start hour</span><input type="number" value={form.start_hour} onChange={(event) => setForm((current) => ({ ...current, start_hour: event.target.value }))} required /></label>
          <label><span>End hour</span><input type="number" value={form.end_hour} onChange={(event) => setForm((current) => ({ ...current, end_hour: event.target.value }))} required /></label>
          <label><span>Room</span><input type="text" value={form.room} onChange={(event) => setForm((current) => ({ ...current, room: event.target.value }))} required /></label>
          <button className="primaryButton compactButton" type="submit" disabled={busy}>{busy ? "Saving..." : submitLabel}</button>
        </form>
        {message ? <p className="muted actionMessage">{message}</p> : null}
      </section>
      <QuestionBuilder questions={questions} setQuestions={setQuestions} questionTypes={[{ value: "text", label: "Text answer" }, { value: "upload", label: "Upload answer" }, { value: "mcq", label: "MCQ" }]} defaultType="text" title="Exam questions" />
    </>
  );
}

function QuizAssignmentPanel({ assignment, questions, busy, message, onSubmit }) {
  const [answers, setAnswers] = useState({});
  useEffect(() => { setAnswers({}); }, [assignment?.id]);
  return (
    <section className="card dataCard formCard">
      <h2>{assignment.name}</h2>
      <p className="muted">{assignment.instructions || "Quiz assignment"}</p>
      <div className="questionList">
        {questions.map((question) => (
          <div key={question.id} className="listCard">
            <strong>{question.question_text}</strong>
            <p>{question.marks} marks</p>
            {["a", "b", "c", "d"].map((optionKey) => (
              <label key={optionKey} className="choiceRow">
                <input type="radio" name={`assignment-question-${question.id}`} checked={answers[question.id] === optionKey} onChange={() => setAnswers((current) => ({ ...current, [question.id]: optionKey }))} />
                <span>{question[`option_${optionKey}`]}</span>
              </label>
            ))}
          </div>
        ))}
      </div>
      <button type="button" className="primaryButton compactButton" disabled={busy} onClick={() => onSubmit(answers)}>{busy ? "Submitting..." : "Submit quiz"}</button>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function UploadAssignmentPanel({ assignment, busy, message, onSubmit }) {
  const [file, setFile] = useState(null);
  const [note, setNote] = useState("");
  useEffect(() => { setFile(null); setNote(""); }, [assignment?.id]);
  return (
    <section className="card dataCard formCard">
      <h2>{assignment.name}</h2>
      <p className="muted">{assignment.instructions || "Upload assignment"}</p>
      {assignment.instruction_file_data ? <a className="ghostButton inlineActionButton" href={dataHrefFromBase64(assignment.instruction_file_data)} download={assignment.instruction_file_name || `${assignment.name}-instructions`}>Download instructions</a> : null}
      <div className="inlineForm">
        <label><span>Upload file if needed</span><input type="file" accept=".pdf,.doc,.docx,.zip,.txt,.png,.jpg,.jpeg" onChange={(event) => setFile(event.target.files?.[0] || null)} /></label>
        <label><span>Submission note</span><textarea value={note} onChange={(event) => setNote(event.target.value)} /></label>
      </div>
      <button type="button" className="primaryButton compactButton" disabled={busy} onClick={() => onSubmit(file, note)}>{busy ? "Submitting..." : "Submit assignment"}</button>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function StudentExamPanel({ exam, questions, busy, message, onSubmit }) {
  const [answers, setAnswers] = useState({});
  useEffect(() => { setAnswers({}); }, [exam?.id]);
  return (
    <section className="card dataCard formCard">
      <h2>{exam.name}</h2>
      <div className="questionList">
        {questions.map((question) => (
          <div key={question.id} className="listCard">
            <strong>{question.question_text}</strong>
            <p>{question.question_type} | {question.marks} marks</p>
            {question.question_type === "mcq" ? (
              ["a", "b", "c", "d"].map((optionKey) => (
                <label key={optionKey} className="choiceRow">
                  <input type="radio" name={`exam-question-${question.id}`} checked={answers[question.id] === optionKey} onChange={() => setAnswers((current) => ({ ...current, [question.id]: optionKey }))} />
                  <span>{question[`option_${optionKey}`]}</span>
                </label>
              ))
            ) : question.question_type === "upload" ? (
              <input type="file" accept=".pdf,.doc,.docx,.txt,.zip,.png,.jpg,.jpeg" onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.files?.[0] || null }))} />
            ) : <textarea value={answers[question.id] || ""} onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))} />}
          </div>
        ))}
      </div>
      <button type="button" className="primaryButton compactButton" disabled={busy} onClick={() => onSubmit(answers)}>{busy ? "Submitting..." : "Submit exam"}</button>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function ExamResultReviewPanel({ result, answers, questions, busy, message, onSave }) {
  const [note, setNote] = useState(result?.note || "");
  const [grades, setGrades] = useState({});
  const answerMap = useMemo(() => new Map((answers || []).map((answer) => [answer.question_id[0], answer])), [answers]);
  useEffect(() => {
    setNote(result?.note || "");
    setGrades(Object.fromEntries((answers || []).map((answer) => [answer.id, String(answer.awarded_marks ?? 0)])));
  }, [result?.id, answers]);
  return (
    <section className="card dataCard formCard">
      <h2>Review exam result</h2>
      <p className="muted">{formatValue(result.exam_id)} | {formatValue(result.student_id)}</p>
      <div className="questionList">
        {questions.map((question) => {
          const answer = answerMap.get(question.id);
          return (
            <div key={question.id} className="listCard">
              <strong>{question.question_text}</strong>
              <p>{question.question_type} | {question.marks} marks</p>
              {question.question_type === "mcq" ? <p>Answer: {answer?.selected_option || "-"}</p> : <>
                {question.question_type === "upload" ? (
                  answer?.file_data ? <a className="ghostButton inlineActionButton" href={dataHrefFromBase64(answer.file_data)} download={answer.file_name || "exam-answer"}>View uploaded answer</a> : <p>Student answer: No file uploaded</p>
                ) : <p>Student answer: {answer?.answer_text || "-"}</p>}
                <label className="dropdownField">
                  <span>Awarded marks</span>
                  <input type="number" value={grades[answer?.id] || ""} onChange={(event) => setGrades((current) => ({ ...current, [answer.id]: event.target.value }))} />
                </label>
              </>}
            </div>
          );
        })}
      </div>
      <label className="dropdownField"><span>Faculty note</span><textarea value={note} onChange={(event) => setNote(event.target.value)} /></label>
      <button type="button" className="primaryButton compactButton" disabled={busy} onClick={() => onSave(Object.entries(grades).map(([answer_id, awarded_marks]) => ({ answer_id: Number(answer_id), awarded_marks: Number(awarded_marks || 0) })), note)}>{busy ? "Saving..." : "Save written marks"}</button>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function StudyAssistantPanel({ courseOptions, busy, message, result, onAnalyze }) {
  const [courseId, setCourseId] = useState(courseOptions[0]?.value || "");
  const [notes, setNotes] = useState("");
  const [attachment, setAttachment] = useState(null);
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    if (!courseId && courseOptions[0]?.value) setCourseId(courseOptions[0].value);
  }, [courseId, courseOptions]);
  useEffect(() => {
    setShowAnswers(false);
  }, [result]);

  return (
    <>
      <section className="card dataCard formCard">
        <h2>AI study assistant</h2>
        <p className="muted">Paste lecture notes or upload a PDF to get a summary, practice MCQs, and a quick gap analysis.</p>
        <div className="inlineForm">
          <label>
            <span>Course</span>
            <select value={courseId} onChange={(event) => setCourseId(event.target.value)}>
              <option value="">General notes</option>
              {courseOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label className="fullSpan">
            <span>Lecture notes</span>
            <textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Paste your lecture notes here..." />
          </label>
          <label className="fullSpan">
            <span>Upload lecture PDF</span>
            <input type="file" accept=".pdf" onChange={(event) => setAttachment(event.target.files?.[0] || null)} />
          </label>
        </div>
        <div className="studyAssistantActions">
          <button type="button" className="primaryButton compactButton" disabled={busy || (!notes.trim() && !attachment)} onClick={() => onAnalyze(notes, courseId ? Number(courseId) : false, attachment)}>
          {busy ? "Analyzing your notes..." : "Analyze notes"}
          </button>
        </div>
        {message ? <p className="muted actionMessage">{message}</p> : null}
      </section>
      {result ? (
        <section className="contentGrid">
          <section className="card dataCard">
            <h2>Summary</h2>
            <div className="stackList">
              {(result.summary || []).map((item, index) => <div key={`${item}-${index}`} className="listCard"><p>{item}</p></div>)}
            </div>
          </section>
          <section className="card dataCard">
            <h2>Gap analysis</h2>
            <p>{result.gap_analysis || "No major study gaps identified."}</p>
          </section>
          <section className="card dataCard fullWidthCard">
            <h2>Practice MCQs</h2>
            <div className="tableActions">
              <button type="button" className="ghostButton tableButton" onClick={() => setShowAnswers((current) => !current)}>
                {showAnswers ? "Hide answers" : "Show answers"}
              </button>
            </div>
            <div className="questionList">
              {(result.mcqs || []).map((mcq, index) => (
                <div key={`${mcq.question}-${index}`} className="listCard">
                  <strong>{index + 1}. {mcq.question}</strong>
                  <p>{(mcq.options || []).join(" / ")}</p>
                  {showAnswers ? <p className="muted">Correct answer: {mcq.answer}</p> : null}
                </div>
              ))}
            </div>
          </section>
        </section>
      ) : null}
    </>
  );
}

function SubmissionReviewPanel({ submission, busy, message, onGenerateFeedback, onSave }) {
  const [score, setScore] = useState(String(submission?.score ?? ""));
  const [feedback, setFeedback] = useState(submission?.feedback || "");

  useEffect(() => {
    setScore(String(submission?.score ?? ""));
    setFeedback(submission?.feedback || "");
  }, [submission?.id]);

  return (
    <section className="card dataCard formCard">
      <h2>Submission review</h2>
      <div className="reviewGrid">
        <div>
          <p><strong>Assignment:</strong> {formatValue(submission.assignment_id)}</p>
          <p><strong>Student:</strong> {formatValue(submission.student_id)}</p>
          <p><strong>Status:</strong> {formatValue(submission.state)}</p>
          <p><strong>Submitted file:</strong> {submission.file_name || "No attachment"}</p>
          <p><strong>Student note:</strong> {submission.feedback || "No note"}</p>
          {submission.file_data ? <a className="ghostButton inlineActionButton" href={dataHrefFromBase64(submission.file_data)} download={submission.file_name || "submission"}>View attachment</a> : null}
        </div>
        <div className="inlineForm">
          <label>
            <span>Score</span>
            <input type="number" value={score} onChange={(event) => setScore(event.target.value)} />
          </label>
          <label className="fullSpan">
            <span>Faculty feedback</span>
            <textarea value={feedback} onChange={(event) => setFeedback(event.target.value)} />
          </label>
          <div className="tableActions">
            <button type="button" className="ghostButton tableButton" disabled={busy || !score} onClick={() => onGenerateFeedback(Number(score), feedback, setFeedback)}>
              Generate feedback
            </button>
            <button type="button" className="primaryButton compactButton" disabled={busy || !score} onClick={() => onSave(Number(score), feedback)}>
              {busy ? "Saving..." : "Save grade"}
            </button>
          </div>
        </div>
      </div>
      {message ? <p className="muted actionMessage">{message}</p> : null}
    </section>
  );
}

function App() {
  const [state, setState] = useState({
    booting: true,
    loggingIn: false,
    session: null,
    databases: [],
    portalData: null,
    loginError: "",
    appError: "",
  });

  async function hydratePortal() {
    const portalData = await fetchPortalData();
    setState((current) => ({ ...current, portalData, appError: "" }));
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        const databases = await loadDatabases();
        if (!databases.length) throw new Error("No Odoo databases were returned by the server");
        try {
          const session = await getSessionInfo();
          setState((current) => ({ ...current, booting: false, databases, session, loginError: "" }));
          await hydratePortal();
        } catch {
          setState((current) => ({ ...current, booting: false, databases, session: null, portalData: null }));
        }
      } catch (error) {
        setState((current) => ({ ...current, booting: false, appError: `${error.message}. Make sure Odoo is running on localhost:8069.` }));
      }
    }
    bootstrap();
  }, []);

  async function handleLogin(form) {
    setState((current) => ({ ...current, loggingIn: true, loginError: "" }));
    try {
      const session = await authenticate(form);
      setState((current) => ({ ...current, session, loggingIn: false, loginError: "" }));
      await hydratePortal();
    } catch (error) {
      setState((current) => ({ ...current, loggingIn: false, loginError: error.message }));
    }
  }

  async function handleLogout() {
    await logout();
    setState((current) => ({ ...current, session: null, portalData: null, loginError: "" }));
  }

  if (state.booting) return <div className="loadingState">Preparing Visionary Minds University portal...</div>;
  if (state.appError) {
    return <div className="loginShell"><div className="card errorCard"><h1>Visionary Minds University</h1><p>{state.appError}</p></div></div>;
  }
  if (!state.session || !state.portalData) return <LoginScreen defaultDb={state.databases[0]} onLogin={handleLogin} loading={state.loggingIn} error={state.loginError} />;
  return <Portal portalData={state.portalData} onLogout={handleLogout} onRefresh={hydratePortal} />;
}

function LoginScreen({ defaultDb, onLogin, loading, error }) {
  const [form, setForm] = useState({ db: defaultDb || "", login: "", password: "" });
  useEffect(() => {
    if (!form.db && defaultDb) setForm((current) => ({ ...current, db: defaultDb }));
  }, [defaultDb, form.db]);
  return (
    <div className="loginShell">
      <div className="loginLayout">
        <section className="loginIntro">
          <div className="loginBrand">
            <span className="brandMark loginBrandMark">VMU</span>
            <div>
              <p className="eyebrow">Visionary Minds University</p>
              <h1>Student and faculty sign in</h1>
            </div>
          </div>
          <p className="tagline">Access academics, exams, fees, library resources, and teaching operations through the Visionary Minds University portal.</p>
          <div className="loginHints">
            <span>Student portal</span>
            <span>Faculty workspace</span>
            <span>Library and academics</span>
            <span>Admin operations</span>
          </div>
        </section>
        <form className="card loginCard" onSubmit={(event) => { event.preventDefault(); onLogin(form); }}>
          <h2>Welcome back</h2>
          <label><span>Login</span><input type="text" value={form.login} onChange={(event) => setForm((current) => ({ ...current, login: event.target.value }))} required /></label>
          <label><span>Password</span><input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} required /></label>
          {error ? <p className="formError">{error}</p> : null}
          <button className="primaryButton" type="submit" disabled={loading}>{loading ? "Signing in..." : "Log in"}</button>
        </form>
      </div>
    </div>
  );
}

function Portal({ portalData, onLogout, onRefresh }) {
  const [activePage, setActivePage] = useState("overview");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedAssignmentId, setSelectedAssignmentId] = useState(null);
  const [selectedSubmissionId, setSelectedSubmissionId] = useState(null);
  const [selectedExamId, setSelectedExamId] = useState(null);
  const [selectedResultId, setSelectedResultId] = useState(null);
  const [activeCourseId, setActiveCourseId] = useState(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [studyAssistantResult, setStudyAssistantResult] = useState(null);
  const [showAtRiskOnly, setShowAtRiskOnly] = useState(false);

  const pages = portalData.pages || {};
  const lookups = portalData.lookups || {};
  const context = portalData.context || {};
  const navItems = useMemo(() => {
    const allowedPages = rolePages[portalData.role] || rolePages.admin;
    return pageMeta.filter((page) => allowedPages.includes(page.id) || (page.id === "library" && portalData.context?.is_librarian));
  }, [portalData.role, portalData.context]);
  const safeActivePage = navItems.some((item) => item.id === activePage) ? activePage : "overview";
  const currentRecords = safeActivePage === "overview" ? [] : (pages[safeActivePage] || []);
  const currentLabel = pageMeta.find((page) => page.id === safeActivePage)?.label || "Overview";
  const isStudent = portalData.role === "student";
  const isFaculty = portalData.role === "faculty";
  const isAdmin = portalData.role === "admin";
  const studentNotifications = isStudent ? buildStudentAlerts(pages) : [];
  const assignmentQuestions = lookups.assignment_questions || [];
  const examQuestions = lookups.exam_questions || [];
  const examAnswers = lookups.exam_answers || [];
  const registrationCourses = lookups.registration_courses || [];
  const departmentOptions = buildOptions(lookups.departments || [], ["code", "name"]);
  const termOptions = buildOptions(lookups.terms || [], ["name", "academic_year"]);
  const courseOptions = buildOptions(pages.courses || [], ["code", "name"]);
  const facultyOptions = buildOptions(pages.faculty || [], ["display_name", "user_login"]);
  const studentOptions = buildOptions(pages.students || [], ["student_number", "name"]);
  const canManageLibrary = isAdmin || Boolean(context.is_librarian);

  useEffect(() => {
    setMessage("");
    setSelectedAssignmentId(null);
    setSelectedSubmissionId(null);
    setSelectedExamId(null);
    setSelectedResultId(null);
    if (safeActivePage !== "study_assistant") setStudyAssistantResult(null);
  }, [safeActivePage]);

  useEffect(() => {
    if (!navItems.some((item) => item.id === activePage)) setActivePage("overview");
  }, [activePage, navItems]);

  useEffect(() => {
    if (!activeCourseId && pages.courses?.length) setActiveCourseId(pages.courses[0].id);
  }, [activeCourseId, pages.courses]);

  useEffect(() => {
    if (!isStudent || typeof window === "undefined" || !("Notification" in window)) return;
    const seen = JSON.parse(window.localStorage.getItem("uni_seen_notifications") || "[]");
    const unseen = studentNotifications.filter((record) => !seen.includes(record.id));
    if (!unseen.length) return;
    if (Notification.permission === "default") {
      Notification.requestPermission();
      return;
    }
    if (Notification.permission === "granted") {
      unseen.forEach((record) => new Notification(record.title, { body: record.body }));
      window.localStorage.setItem("uni_seen_notifications", JSON.stringify([...seen, ...unseen.map((record) => record.id)]));
    }
  }, [isStudent, studentNotifications]);

  async function runAction(action, successMessage = "Saved.") {
    setBusy(true);
    setMessage("");
    try {
      await action();
      await onRefresh();
      setMessage(successMessage);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  function renderStudentOverview() {
    const assignments = pages.assignments || [];
    const submissions = pages.submissions || [];
    const courses = pages.courses || [];
    const timetable = pages.timetable || [];
    const faculty = pages.faculty || [];
    const fees = pages.fees || [];
    const exams = pages.exams || [];
    const today = new Date();
    const submittedAssignmentIds = new Set(submissions.filter((record) => Array.isArray(record.assignment_id)).map((record) => record.assignment_id[0]));
    const pendingAssignments = assignments.filter((assignment) => !submittedAssignmentIds.has(assignment.id)).sort((left, right) => String(left.due_date || "").localeCompare(String(right.due_date || "")));
    const overdueAssignments = pendingAssignments.filter((assignment) => assignment.due_date && new Date(assignment.due_date) < today);
    const pendingFees = fees.filter((record) => Number(record.balance_due || 0) > 0 && record.state !== "paid");
    const upcomingExams = exams.filter((record) => record.exam_date && new Date(record.exam_date) >= new Date(today.toDateString())).sort((left, right) => String(left.exam_date || "").localeCompare(String(right.exam_date || "")));
    const activeCourse = courses.find((course) => course.id === activeCourseId) || courses[0];
    const activeCourseTimetable = activeCourse ? timetable.filter((slot) => Array.isArray(slot.course_id) && slot.course_id[0] === activeCourse.id) : [];
    const activeCourseAssignments = activeCourse ? assignments.filter((assignment) => Array.isArray(assignment.course_id) && assignment.course_id[0] === activeCourse.id) : [];
    const activeFaculty = activeCourse && Array.isArray(activeCourse.faculty_id) ? faculty.find((record) => record.id === activeCourse.faculty_id[0]) : null;
    return (
      <>
        <section className="heroPanel">
          <div>
            <p className="eyebrow">{roleTitles.student}</p>
            <h1>{portalData.dashboard.university_name}</h1>
            <p className="tagline">{portalData.dashboard.tagline}</p>
          </div>
          <div className="heroActions">
            <button type="button" className="ghostButton notificationButton" onClick={() => setNotificationsOpen(true)}>Notifications {studentNotifications.length ? `(${studentNotifications.length})` : ""}</button>
            <div className="badge">student</div>
          </div>
        </section>
        {message ? <SectionMessage message={message} /> : null}
        <section className="contentGrid">
          <article className="card dataCard"><h2>Undone and overdue assignments</h2>{pendingAssignments.length ? <div className="stackList">{pendingAssignments.map((assignment) => <div key={assignment.id} className={overdueAssignments.some((item) => item.id === assignment.id) ? "listCard urgent" : "listCard"}><strong>{assignment.name}</strong><p>{formatValue(assignment.course_id)} | due {formatValue(assignment.due_date)}</p><span className="inlineBadge">{overdueAssignments.some((item) => item.id === assignment.id) ? "Overdue" : "Pending"}</span></div>)}</div> : <p className="muted">No undone assignments right now.</p>}</article>
          <article className="card dataCard"><h2>Pending fees</h2>{pendingFees.length ? <div className="stackList">{pendingFees.map((fee) => <div key={fee.id} className="listCard"><strong>{fee.name}</strong><p>Balance due {formatValue(fee.balance_due)} | due {formatValue(fee.due_date)}</p></div>)}</div> : <p className="muted">No pending fees right now.</p>}</article>
          <article className="card dataCard"><h2>Scheduled exams</h2>{upcomingExams.length ? <div className="stackList">{upcomingExams.map((exam) => <div key={exam.id} className="listCard"><strong>{exam.name}</strong><p>{formatValue(exam.course_id)} | {formatValue(exam.exam_date)} | {formatValue(exam.start_hour)} - {formatValue(exam.end_hour)}</p></div>)}</div> : <p className="muted">No upcoming exams scheduled.</p>}</article>
          <article className="card dataCard"><h2>Your classes</h2>{courses.length ? <div className="stackList">{courses.map((course) => { const isOpen = activeCourse && course.id === activeCourse.id; return <button key={course.id} type="button" className={isOpen ? "courseAccordion active" : "courseAccordion"} onClick={() => setActiveCourseId(isOpen ? null : course.id)}><span>{formatValue(course.code)}</span><strong>{formatValue(course.name)}</strong></button>; })}</div> : <p className="muted">No enrolled classes yet.</p>}</article>
        </section>
        {activeCourse ? <section className="contentGrid"><article className="card dataCard"><h2>{formatValue(activeCourse.name)}</h2><p className="muted">Instructor: {activeFaculty ? `${formatValue(activeFaculty.display_name)} (${formatValue(activeFaculty.user_login)})` : formatValue(activeCourse.faculty_id)}</p><h3>Class timings</h3>{activeCourseTimetable.length ? <ul className="bulletList">{activeCourseTimetable.map((slot) => <li key={slot.id}>{formatValue(slot.weekday)} {formatValue(slot.start_hour)} - {formatValue(slot.end_hour)} | {formatValue(slot.room)}</li>)}</ul> : <p className="muted">No timetable slots for this class yet.</p>}</article><article className="card dataCard"><h2>Subject assignments</h2>{activeCourseAssignments.length ? <div className="stackList">{activeCourseAssignments.map((assignment) => <div key={assignment.id} className="listCard"><strong>{assignment.name}</strong><p>{assignment.assignment_type} | due {formatValue(assignment.due_date)}</p><p className="muted">{formatValue(assignment.instructions)}</p></div>)}</div> : <p className="muted">No assignments for this subject yet.</p>}</article></section> : null}
      </>
    );
  }

    function renderStudentsPage() {
      if (isFaculty) {
        const filteredRecords = showAtRiskOnly ? currentRecords.filter((record) => ["high", "critical"].includes(String(record.risk_level || "").toLowerCase())) : currentRecords;
      const groupedRecords = filteredRecords.reduce((accumulator, record) => {
        const key = record.course || "Unassigned course";
        accumulator[key] = accumulator[key] || [];
        accumulator[key].push(record);
        return accumulator;
      }, {});
      const courseNames = Object.keys(groupedRecords);
      return (
        <>
          <SectionHeader title="Students by course" />
          <section className="card dataCard">
            <div className="tableActions">
              <label className="choiceRow">
                <input type="checkbox" checked={showAtRiskOnly} onChange={(event) => setShowAtRiskOnly(event.target.checked)} />
                <span>Show only at-risk students</span>
              </label>
            </div>
            {message ? <p className="muted actionMessage">{message}</p> : null}
          </section>
          {courseNames.length ? courseNames.map((courseName) => (
            <DataTable
              key={courseName}
              title={courseName}
              records={groupedRecords[courseName]}
              hiddenColumns={["course", "course_code"]}
            />
          )) : <section className="card dataCard"><p className="muted">No students registered in your subjects yet.</p></section>}
        </>
      );
      }
      const atRiskRecords = currentRecords.filter((record) => ["high", "critical"].includes(String(record.risk_level || "").toLowerCase()));
      return (
        <>
          <SectionHeader title={currentLabel} />
          {isAdmin ? (
            <>
              <section className="card dataCard">
                <div className="tableActions">
                  <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => triggerRiskScan(), "At-risk scan completed.")}>Run at-risk scan</button>
                </div>
                {message ? <p className="muted actionMessage">{message}</p> : null}
              </section>
              <SimpleForm title="Add student" busy={busy} message="" submitLabel="Create student" fields={[{ name: "name", label: "Full name", required: true }, { name: "login", label: "Username", required: true }, { name: "password", label: "Password", required: true, type: "password" }, { name: "email", label: "Email", type: "email" }, { name: "student_number", label: "Student number", required: true }, { name: "department_id", label: "Department", required: true, type: "select", options: departmentOptions }, { name: "advisor_id", label: "Advisor", type: "select", options: facultyOptions }, { name: "term_id", label: "Term", required: true, type: "select", options: termOptions }]} onSubmit={(form, reset) => runAction(async () => { await createStudent({ ...form, department_id: Number(form.department_id), advisor_id: form.advisor_id ? Number(form.advisor_id) : false, term_id: Number(form.term_id), state: "enrolled" }); reset(); })} />
              {atRiskRecords.length ? <DataTable title="At-risk students needing intervention" records={atRiskRecords} /> : null}
            </>
          ) : <SectionMessage message={message} />}
          <DataTable title={currentLabel} records={currentRecords} />
        </>
      );
  }
  function renderFacultyPage() { return (<><SectionHeader title={currentLabel} />{isAdmin ? <SimpleForm title="Add faculty member" busy={busy} message={message} submitLabel="Create faculty" fields={[{ name: "name", label: "Full name", required: true, defaultValue: "Amina Rahman" }, { name: "title", label: "Title", required: true, defaultValue: "Dr." }, { name: "login", label: "Username", required: true }, { name: "password", label: "Password", required: true, type: "password" }, { name: "email", label: "Email", type: "email" }, { name: "department_id", label: "Department", required: true, type: "select", options: departmentOptions }, { name: "max_load_hours", label: "Max load hours", required: true, type: "number", defaultValue: "12" }]} onSubmit={(form, reset) => runAction(async () => { await createFaculty({ ...form, department_id: Number(form.department_id), max_load_hours: Number(form.max_load_hours) }); reset(); })} /> : <SectionMessage message={message} />}<DataTable title={currentLabel} records={currentRecords} /></>); }
  function renderCoursesPage() {
    if (isStudent) {
      const registrations = pages.registrations || [];
      const registrationByCourseId = new Map(registrations.filter((record) => Array.isArray(record.course_id)).map((record) => [record.course_id[0], record]));
      const catalogCourses = registrationCourses.map((course) => ({
        ...course,
        registration_status: registrationByCourseId.get(course.id)?.status || false,
        registered_on: registrationByCourseId.get(course.id)?.registered_on || false,
      }));
      return (
        <>
          <SectionHeader title="Courses" />
          <SectionMessage message={message} />
          <section className="contentGrid">
            <section className="card dataCard">
              <h2>Course catalog</h2>
              {catalogCourses.length ? (
                <div className="stackList">
                  {catalogCourses.map((course) => {
                    const alreadyRegistered = Boolean(course.registration_status);
                    return (
                      <div key={course.id} className="listCard">
                        <strong>{formatValue(course.code)} | {formatValue(course.name)}</strong>
                        <p>{formatValue(course.faculty_id)} | {formatValue(course.credit_hours)} credit hours | seats {formatValue(course.seat_limit)}</p>
                        <div className="tableActions">
                          {alreadyRegistered ? <span className="inlineBadge">Already registered</span> : <button type="button" className="ghostButton inlineActionButton" disabled={busy} onClick={() => runAction(() => createRegistration({ course_id: course.id, term_id: Array.isArray(course.term_id) ? course.term_id[0] : false }))}>Register</button>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : <p className="muted">No courses available right now.</p>}
            </section>
            <DataTable title="My registered courses" records={currentRecords} />
          </section>
        </>
      );
    }
    return (
      <>
        <SectionHeader title={currentLabel} />
        {isAdmin ? (
          <section className="contentGrid">
            <SimpleForm title="Add course" busy={busy} message={message} submitLabel="Create course" fields={[{ name: "code", label: "Course code", required: true }, { name: "name", label: "Course name", required: true }, { name: "department_id", label: "Department", required: true, type: "select", options: departmentOptions }, { name: "faculty_id", label: "Faculty", required: true, type: "select", options: facultyOptions }, { name: "term_id", label: "Term", required: true, type: "select", options: termOptions }, { name: "credit_hours", label: "Credit hours", required: true, type: "number", defaultValue: "3" }, { name: "seat_limit", label: "Seat limit", required: true, type: "number", defaultValue: "30" }]} onSubmit={(form, reset) => runAction(async () => { await createCourse({ ...form, department_id: Number(form.department_id), faculty_id: Number(form.faculty_id), term_id: Number(form.term_id), credit_hours: Number(form.credit_hours), seat_limit: Number(form.seat_limit) }); reset(); })} />
            <SimpleForm title="Assign course to faculty" busy={busy} message={message} submitLabel="Save assignment" fields={[{ name: "course_id", label: "Course", required: true, type: "select", options: courseOptions }, { name: "faculty_id", label: "Faculty", required: true, type: "select", options: facultyOptions }]} onSubmit={(form, reset) => runAction(async () => { await updateCourse(Number(form.course_id), { faculty_id: Number(form.faculty_id) }); reset(); })} />
          </section>
        ) : <SectionMessage message={message} />}
        <DataTable title={currentLabel} records={currentRecords} />
        {isAdmin ? <DataTable title="Course registrations" records={pages.registrations || []} /> : null}
      </>
    );
  }

  function renderAssignmentsPage() {
    const submissions = pages.submissions || [];
    const studentSubmissionMap = new Map(submissions.filter((record) => Array.isArray(record.assignment_id)).map((record) => [record.assignment_id[0], record]));
    const pendingAssignments = isStudent ? currentRecords.filter((record) => !studentSubmissionMap.has(record.id)) : currentRecords;
    const completedAssignments = isStudent ? currentRecords.filter((record) => studentSubmissionMap.has(record.id)) : [];
    const selectedAssignment = currentRecords.find((record) => record.id === selectedAssignmentId);
    const selectedAssignmentQuestions = assignmentQuestions.filter((question) => Array.isArray(question.assignment_id) && question.assignment_id[0] === selectedAssignmentId);
    const assignmentEditorForm = selectedAssignment ? {
      name: selectedAssignment.name || "",
      course_id: Array.isArray(selectedAssignment.course_id) ? String(selectedAssignment.course_id[0]) : "",
      term_id: Array.isArray(selectedAssignment.term_id) ? String(selectedAssignment.term_id[0]) : "",
      due_date: selectedAssignment.due_date || "",
      total_marks: String(selectedAssignment.total_marks || "100"),
      instructions: selectedAssignment.instructions || "",
      assignment_type: selectedAssignment.assignment_type || "upload",
      instruction_file: null,
      instruction_file_name: selectedAssignment.instruction_file_name || "",
      instruction_file_data: selectedAssignment.instruction_file_data || false,
    } : null;
    return (
      <>
        <SectionHeader title={currentLabel} />
        {(isFaculty || isAdmin) ? (selectedAssignment ? <><AssignmentCreationPanel busy={busy} message={message} courseOptions={courseOptions} termOptions={termOptions} panelTitle="Edit assignment" submitLabel="Save assignment" initialForm={assignmentEditorForm} initialQuestions={selectedAssignment.assignment_type === "quiz" ? selectedAssignmentQuestions.map((question) => ({ ...question, marks: String(question.marks || 1) })) : []} initialKey={`assignment-${selectedAssignment.id}`} onCreate={(form, questions) => runAction(async () => { const file = form.instruction_file; await updateAssignment(selectedAssignment.id, { name: form.name, course_id: Number(form.course_id), term_id: Number(form.term_id), due_date: form.due_date, total_marks: Number(form.total_marks), instructions: form.instructions, assignment_type: form.assignment_type, instruction_file_name: file ? file.name : form.instruction_file_name || "", instruction_file_data: file ? await fileToBase64(file) : form.instruction_file_data || false, questions, state: "draft" }); })} /><section className="card dataCard"><div className="tableActions">{selectedAssignment.state !== "published" ? <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(async () => { await publishAssignment(selectedAssignment.id); setSelectedAssignmentId(null); })}>Publish</button> : null}<button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(async () => { await deleteAssignment(selectedAssignment.id); setSelectedAssignmentId(null); })}>Delete</button><button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedAssignmentId(null)}>Close editor</button></div></section></> : <AssignmentCreationPanel busy={busy} message={message} courseOptions={courseOptions} termOptions={termOptions} onCreate={(form, questions, reset) => runAction(async () => { const file = form.instruction_file; await createAssignment({ name: form.name, course_id: Number(form.course_id), term_id: Number(form.term_id), due_date: form.due_date, total_marks: Number(form.total_marks), instructions: form.instructions, assignment_type: form.assignment_type, instruction_file_name: file ? file.name : "", instruction_file_data: file ? await fileToBase64(file) : false, questions, state: "draft" }); reset(); })} />) : null}
        {isStudent && selectedAssignment ? (selectedAssignment.assignment_type === "quiz" ? <QuizAssignmentPanel assignment={selectedAssignment} questions={selectedAssignmentQuestions} busy={busy} message={message} onSubmit={(answers) => runAction(async () => { await createSubmission({ assignment_id: selectedAssignment.id, quiz_answers: selectedAssignmentQuestions.map((question) => ({ question_id: question.id, selected_option: answers[question.id] || false })) }); setSelectedAssignmentId(null); })} /> : <UploadAssignmentPanel assignment={selectedAssignment} busy={busy} message={message} onSubmit={(file, note) => runAction(async () => { await createSubmission({ assignment_id: selectedAssignment.id, file_name: file ? file.name : "", file_data: file ? await fileToBase64(file) : false, feedback: note }); setSelectedAssignmentId(null); })} />) : (!isFaculty && !isAdmin ? <SectionMessage message={message} /> : null)}
        {isStudent ? (<>{pendingAssignments.length ? <DataTable title="Uncompleted assignments" records={pendingAssignments} actions={(record) => <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedAssignmentId(record.id)}>{record.assignment_type === "quiz" ? "Start quiz" : "Submit"}</button>} hiddenColumns={["faculty_id", "owner_login", "term_id", "submission_count", "question_count", "instructions", "instruction_file_name"]} /> : null}{completedAssignments.length ? <DataTable title="Completed assignments" records={completedAssignments.map((record) => { const submission = studentSubmissionMap.get(record.id); return { ...record, submission_state: submission?.state || "-", submitted_file: submission?.file_name || "-", score: submission?.score ?? "-" }; })} hiddenColumns={["faculty_id", "owner_login", "term_id", "submission_count", "question_count", "instructions", "instruction_file_name"]} /> : null}{!pendingAssignments.length && !completedAssignments.length ? <section className="card dataCard"><p className="muted">No assignments available yet.</p></section> : null}</>) : <DataTable title={currentLabel} records={currentRecords} hiddenColumns={["faculty_id", "owner_login", "term_id", "submission_count", "question_count", "instructions", "instruction_file_name"]} actions={(record) => <div className="tableActions"><button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedAssignmentId(record.id)}>Edit</button>{record.state !== "published" ? <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => publishAssignment(record.id))}>Publish</button> : null}<button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => deleteAssignment(record.id))}>Delete</button></div>} />}
      </>
    );
  }

  function renderSubmissionsPage() {
    const ungradedRecords = currentRecords.filter((record) => record.state !== "graded");
    const gradedRecords = currentRecords.filter((record) => record.state === "graded");
    const selectedSubmission = currentRecords.find((record) => record.id === selectedSubmissionId);
    return (
      <>
        <SectionHeader title={currentLabel} />
        {selectedSubmission ? <SubmissionReviewPanel submission={selectedSubmission} busy={busy} message={message} onGenerateFeedback={async (score, feedback, setFeedback) => {
          setBusy(true);
          setMessage("");
          try {
            const result = await requestFeedbackDraft(formatValue(selectedSubmission.assignment_id), formatValue(selectedSubmission.student_id), score, feedback);
            setFeedback(result.feedback || "");
          } catch (error) {
            setMessage(error.message);
          } finally {
            setBusy(false);
          }
        }} onSave={(score, feedback) => runAction(async () => { await gradeSubmission(selectedSubmission.id, Number(score), feedback); setSelectedSubmissionId(null); })} /> : <SectionMessage message={message} />}
        {ungradedRecords.length ? <DataTable title="Ungraded submissions" records={ungradedRecords} actions={(record) => <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedSubmissionId(record.id)}>Review and grade</button>} /> : null}
        {gradedRecords.length ? <DataTable title="Completed grading" records={gradedRecords} /> : null}
        {!ungradedRecords.length && !gradedRecords.length ? <section className="card dataCard"><p className="muted">No submissions available yet.</p></section> : null}
      </>
    );
  }

  function renderStudyAssistantPage() {
    return (
      <>
        <SectionHeader title={currentLabel} />
        <StudyAssistantPanel
          courseOptions={courseOptions}
          busy={busy}
          message={message}
          result={studyAssistantResult}
          onAnalyze={(notes, courseId, file) => runAction(async () => {
            const result = await requestStudyAssistant(
              notes,
              courseId || false,
              file ? file.name : "",
              file ? await fileToBase64(file) : false,
            );
            setStudyAssistantResult(result);
          })}
        />
      </>
    );
  }

  function renderExamsPage() {
    const studentResultsByExam = new Map((pages.results || []).filter((record) => Array.isArray(record.exam_id)).map((record) => [record.exam_id[0], record]));
    const selectedExam = currentRecords.find((record) => record.id === selectedExamId);
    const selectedExamQuestions = examQuestions.filter((question) => Array.isArray(question.exam_id) && question.exam_id[0] === selectedExamId);
    const examEditorForm = selectedExam ? {
      name: selectedExam.name || "",
      course_id: Array.isArray(selectedExam.course_id) ? String(selectedExam.course_id[0]) : "",
      term_id: Array.isArray(selectedExam.term_id) ? String(selectedExam.term_id[0]) : "",
      exam_date: selectedExam.exam_date || "",
      start_hour: String(selectedExam.start_hour || "10"),
      end_hour: String(selectedExam.end_hour || "12"),
      room: selectedExam.room || "Online",
      capacity: "200",
    } : null;
    return (
      <>
        <SectionHeader title={currentLabel} />
        {(isFaculty || isAdmin) ? (selectedExam ? <><ExamCreationPanel busy={busy} message={message} courseOptions={courseOptions} termOptions={termOptions} panelTitle="Edit exam" submitLabel="Save exam" initialForm={examEditorForm} initialQuestions={selectedExamQuestions.map((question) => ({ ...question, marks: String(question.marks || 1) }))} initialKey={`exam-${selectedExam.id}`} onCreate={(form, questions) => runAction(async () => { await updateExam(selectedExam.id, { name: form.name, course_id: Number(form.course_id), term_id: Number(form.term_id), exam_date: form.exam_date, start_hour: Number(form.start_hour), end_hour: Number(form.end_hour), room: form.room, delivery_mode: "online", questions, state: "draft" }); })} /><section className="card dataCard"><div className="tableActions">{selectedExam.state !== "visible" ? <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(async () => { await publishExam(selectedExam.id); setSelectedExamId(null); })}>Publish</button> : null}<button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(async () => { await deleteExam(selectedExam.id); setSelectedExamId(null); })}>Delete</button><button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedExamId(null)}>Close editor</button></div></section></> : <ExamCreationPanel busy={busy} message={message} courseOptions={courseOptions} termOptions={termOptions} onCreate={(form, questions, reset) => runAction(async () => { await createExam({ name: form.name, course_id: Number(form.course_id), term_id: Number(form.term_id), exam_date: form.exam_date, start_hour: Number(form.start_hour), end_hour: Number(form.end_hour), room: form.room, capacity: Number(form.capacity), delivery_mode: "online", questions, state: "draft" }); reset(); })} />) : null}
        {isStudent && selectedExam ? <StudentExamPanel exam={selectedExam} questions={selectedExamQuestions} busy={busy} message={message} onSubmit={(answers) => runAction(async () => { await submitExam(selectedExam.id, await Promise.all(selectedExamQuestions.map(async (question) => ({ question_id: question.id, selected_option: question.question_type === "mcq" ? answers[question.id] || false : false, answer_text: question.question_type === "text" ? answers[question.id] || "" : "", file_name: question.question_type === "upload" && answers[question.id] ? answers[question.id].name : "", file_data: question.question_type === "upload" && answers[question.id] ? await fileToBase64(answers[question.id]) : false })))); setSelectedExamId(null); })} /> : null}
        <DataTable title={currentLabel} records={currentRecords} hiddenColumns={["term_id", "delivery_mode", "question_count", "result_state"]} actions={(record) => {
          if (isStudent) return studentResultsByExam.has(record.id) ? <span className="inlineBadge">Submitted</span> : <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedExamId(record.id)}>Take exam</button>;
          if (isFaculty || isAdmin) return <div className="tableActions"><button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedExamId(record.id)}>Edit</button>{record.state !== "visible" ? <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => publishExam(record.id))}>Publish</button> : null}<button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => deleteExam(record.id))}>Delete</button></div>;
          return null;
        }} />
      </>
    );
  }

  function renderResultsPage() {
    const selectedResult = currentRecords.find((record) => record.id === selectedResultId);
    const selectedResultAnswers = examAnswers.filter((answer) => Array.isArray(answer.result_id) && answer.result_id[0] === selectedResultId);
    const selectedResultQuestions = selectedResult ? examQuestions.filter((question) => Array.isArray(question.exam_id) && question.exam_id[0] === selectedResult.exam_id[0]) : [];
    return (
      <>
        <SectionHeader title={currentLabel} />
        {(isFaculty || isAdmin) && selectedResult ? <ExamResultReviewPanel result={selectedResult} answers={selectedResultAnswers} questions={selectedResultQuestions} busy={busy} message={message} onSave={(grades, note) => runAction(async () => { await gradeWrittenExam(selectedResult.id, grades, note); setSelectedResultId(null); })} /> : <SectionMessage message={message} />}
        <DataTable title={currentLabel} records={currentRecords} actions={(isFaculty || isAdmin) ? (record) => <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => setSelectedResultId(record.id)}>Review result</button> : null} />
      </>
    );
  }

  function renderResitsPage() {
    const resultOptions = buildOptions(pages.results || [], ["exam_id", "student_id"]);
    return (<><SectionHeader title={currentLabel} />{isStudent ? <SimpleForm title="Request resit" busy={busy} message={message} submitLabel="Request resit" fields={[{ name: "exam_result_id", label: "Exam result", required: true, type: "select", options: resultOptions }, { name: "reason", label: "Reason", required: true, type: "textarea" }]} onSubmit={(form, reset) => runAction(async () => { await createResit({ exam_result_id: Number(form.exam_result_id), student_id: context.student_id, reason: form.reason }); reset(); })} /> : <SectionMessage message={message} />}<DataTable title={currentLabel} records={currentRecords} /></>);
  }

  function renderFeesPage() {
    const pendingFees = currentRecords.filter((record) => Number(record.balance_due || 0) > 0 && record.state !== "paid");
    const paidFees = currentRecords.filter((record) => Number(record.balance_due || 0) <= 0 || record.state === "paid");
    return (<><SectionHeader title={currentLabel} /><SectionMessage message={message} />{pendingFees.length ? <DataTable title="Pending fees" records={pendingFees} actions={isStudent ? (record) => <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => runAction(() => payFee(record.id, Math.min(Number(record.balance_due || 0), 500)))}>Pay 500</button> : null} /> : null}{paidFees.length ? <DataTable title="Paid fees" records={paidFees} /> : null}{!pendingFees.length && !paidFees.length ? <section className="card dataCard"><p className="muted">No fee records available yet.</p></section> : null}</>);
  }

  function renderLibraryPage() {
    return (
      <>
        <SectionHeader title={currentLabel} />
        <SectionMessage message={message} />
        <section className="contentGrid">
          <DataTable title="Available resources" records={pages.libraryItems || []} />
          <DataTable
            title="Borrowed and return status"
            records={pages.libraryLoans || []}
            actions={canManageLibrary ? (record) => (
              <div className="tableActions">
                {record.state !== "returned" ? <button type="button" className="ghostButton tableButton" disabled={busy} onClick={() => {
                  const fineAmount = window.prompt("Fine amount for this return", String(record.fine_amount || 0));
                  if (fineAmount === null) return;
                  runAction(() => updateLibraryLoan(record.id, "returned", Number(fineAmount || 0)));
                }}>Mark returned</button> : null}
              </div>
            ) : null}
          />
        </section>
      </>
    );
  }

  function renderPage() {
    if (safeActivePage === "overview") return isStudent ? renderStudentOverview() : (isFaculty ? <FacultyOverview dashboard={portalData.dashboard} pages={pages} /> : <OverviewPage dashboard={portalData.dashboard} />);
    if (safeActivePage === "students") return renderStudentsPage();
    if (safeActivePage === "faculty") return renderFacultyPage();
    if (safeActivePage === "courses") return renderCoursesPage();
    if (safeActivePage === "study_assistant") return renderStudyAssistantPage();
    if (safeActivePage === "assignments") return renderAssignmentsPage();
    if (safeActivePage === "submissions") return renderSubmissionsPage();
    if (safeActivePage === "exams") return renderExamsPage();
    if (safeActivePage === "results") return renderResultsPage();
    if (safeActivePage === "resits") return renderResitsPage();
    if (safeActivePage === "fees") return renderFeesPage();
    if (safeActivePage === "library") return renderLibraryPage();
    if (safeActivePage === "timetable") {
      return (
        <>
          <SectionHeader title={isFaculty ? "My Teaching Timetable" : currentLabel} />
          <SectionMessage message={message} />
          <TimetableWeekView title={isFaculty ? "My classes this week" : "Weekly class calendar"} records={currentRecords} emptyMessage="No timetable slots available yet." />
        </>
      );
    }
    return (<><SectionHeader title={currentLabel} /><SectionMessage message={message} /><DataTable title={currentLabel} records={currentRecords} /></>);
  }

  return (
    <div className="portalShell">
      {isStudent ? <NotificationDrawer open={notificationsOpen} onClose={() => setNotificationsOpen(false)} notifications={studentNotifications} /> : null}
      <aside className="sidebar">
        <div className="sidebarBrand">
          <span className="brandMark">{getAcronym(portalData.dashboard.university_name)}</span>
          <div><strong>{portalData.dashboard.university_name}</strong><p>{roleTitles[portalData.role]}</p></div>
        </div>
        <nav className="sidebarNav">{navItems.map((item) => <button key={item.id} type="button" className={item.id === safeActivePage ? "navButton active" : "navButton"} onClick={() => setActivePage(item.id)}>{item.label}</button>)}</nav>
        <button className="ghostButton sidebarLogout" type="button" onClick={onLogout}>Log out</button>
      </aside>
      <main className="mainContent">{renderPage()}</main>
    </div>
  );
}

export default App;
