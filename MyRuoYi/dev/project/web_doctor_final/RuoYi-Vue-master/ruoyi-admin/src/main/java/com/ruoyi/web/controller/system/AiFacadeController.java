package com.ruoyi.web.controller.system;

import com.alibaba.fastjson2.JSONObject;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.domain.Recovery;
import com.ruoyi.system.service.IPatientService;
import com.ruoyi.system.service.IRecoveryService;
import com.ruoyi.system.service.ISysPatientFamilyService;
import com.ruoyi.web.service.ai.AiGatewayService;
import com.ruoyi.web.service.ai.RecoveryAchievementService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.format.DateTimeFormatter;

import java.util.ArrayList;
import java.util.Comparator;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@RestController
public class AiFacadeController extends BaseController {

    private static final Logger log = LoggerFactory.getLogger(AiFacadeController.class);
    private static final LocalDate DISPLAY_BASE_DATE = LocalDate.of(2026, 3, 10);
    private static final LocalDate SOURCE_BASE_DATE = LocalDate.of(2016, 4, 15);
    private static final LocalDate SOURCE_END_DATE = LocalDate.of(2016, 5, 9);

    @Autowired
    private AiGatewayService aiGatewayService;

    @Autowired
    private ISysPatientFamilyService sysPatientFamilyService;

    @Autowired
    private RecoveryAchievementService recoveryAchievementService;

    @Autowired
    private IPatientService patientService;

    @Autowired
    private IRecoveryService recoveryService;

    @Value("${ai.service.report-root}")
    private String reportRoot;

    @GetMapping("/system/heart-twin/realtime")
    public AjaxResult patientHeartTwinRealtime(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object data = aiGatewayService.heartTwinRealtime(resolved, "patient");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/system/heart-twin/forecast")
    public AjaxResult patientHeartTwinForecast(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object data = aiGatewayService.heartTwinForecast(resolved, "patient");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/family/patient/heart-twin/realtime")
    public AjaxResult familyHeartTwinRealtime(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object data = aiGatewayService.heartTwinRealtime(patientId, "family");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/family/patient/heart-twin/forecast")
    public AjaxResult familyHeartTwinForecast(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object data = aiGatewayService.heartTwinForecast(patientId, "family");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/system/recovery-achievement/current")
    public AjaxResult recoveryAchievementCurrent(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }

        JSONObject decision = aiGatewayService.healthyLifeDecision(
                resolved,
                LocalDate.now().toString(),
                Collections.<String, Object>emptyMap()
        );

        boolean healthyToday = decision.getBooleanValue("isHealthyLife");
        Map<String, Object> data = recoveryAchievementService.buildCurrent(resolved, healthyToday);
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/family/patient/recovery-achievement/current")
    public AjaxResult familyRecoveryAchievementCurrent(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }

        JSONObject decision = aiGatewayService.healthyLifeDecision(
            patientId,
            LocalDate.now().toString(),
            Collections.<String, Object>emptyMap()
        );

        boolean healthyToday = decision.getBooleanValue("isHealthyLife");
        Map<String, Object> data = recoveryAchievementService.buildCurrent(patientId, healthyToday);
        return AjaxResult.success("success", data);
    }

    @GetMapping("/system/risk/predict")
    public AjaxResult patientRiskPredict(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object raw = aiGatewayService.riskPredict(resolved, "patient");
        return AjaxResult.success("success", buildRiskModule(raw, resolved));
    }

    @GetMapping("/system/risk/predict/history")
    public AjaxResult patientRiskPredictHistory(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }

        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(resolved, "patient", "daily")) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildRiskHistoryItemFromReport(item, resolved);
            if (!row.isEmpty()) {
                rows.add(row);
            }
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/api/family/patient/risk/predict")
    public AjaxResult familyRiskPredict(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object raw = aiGatewayService.riskPredict(patientId, "family");
        return AjaxResult.success("success", buildRiskModule(raw, patientId));
    }

    @GetMapping("/api/family/patient/risk/predict/history")
    public AjaxResult familyRiskPredictHistory(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }

        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(patientId, "family", "daily")) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildRiskHistoryItemFromReport(item, patientId);
            if (!row.isEmpty()) {
                rows.add(row);
            }
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/api/doctor/patient/risk/predict")
    public AjaxResult doctorRiskPredict(@RequestParam("patientId") Long patientId) {
        try {
            Object raw = aiGatewayService.riskPredict(patientId, "doctor");
            return AjaxResult.success("success", buildRiskModule(raw, patientId));
        } catch (Exception ex) {
            log.warn("[DOCTOR_RISK_FALLBACK] patientId={}, err={}", patientId, ex.getMessage());

            JSONObject report = loadMappedLocalDailyReport(patientId, "doctor");
            if (report == null) {
                return AjaxResult.success("success", buildEmptyRiskModule(patientId));
            }

            String sourceDate = resolveMappedDailySourceDate(LocalDate.now());
            String displayDate = mapSourceDateToDisplayDate(sourceDate);
            Map<String, Object> mapped = buildRiskHistoryItemFromReport(
                new ReportHistoryItem(sourceDate, displayDate, report),
                patientId
            );

            if (mapped.isEmpty()) {
                return AjaxResult.success("success", buildEmptyRiskModule(patientId));
            }
            return AjaxResult.success("success", mapped);
        }
    }

    @GetMapping("/api/doctor/patient/ai-patient/list")
    public AjaxResult doctorAiPatientList(@RequestParam(value = "patientId", required = false) Long patientId,
                                          @RequestParam(value = "patientName", required = false) String patientName) {
        String mappedDate = resolveMappedDailySourceDate(LocalDate.now());
        List<Long> mappedPatients = resolveDoctorMappedPatientsByDate(mappedDate);

        if (mappedPatients.isEmpty()) {
            return AjaxResult.success("success", new ArrayList<>());
        }

        String byName = patientName == null ? "" : patientName.trim();
        Map<Long, String> idNameMap = new HashMap<>();

        Patient query = new Patient();
        if (!byName.isEmpty()) {
            query.setPatientName(byName);
        }
        List<Patient> patients = patientService.selectPatientList(query);
        for (Patient p : patients) {
            if (p != null && p.getPatientId() != null) {
                idNameMap.put(p.getPatientId(), p.getPatientName());
            }
        }

        List<Map<String, Object>> rows = new ArrayList<>();
        for (Long pid : mappedPatients) {
            if (patientId != null && !patientId.equals(pid)) {
                continue;
            }

            String name = idNameMap.get(pid);
            if ((name == null || name.trim().isEmpty())) {
                Patient one = patientService.selectPatientByPatientId(pid);
                if (one != null) {
                    name = one.getPatientName();
                }
            }

            if ((name == null || name.trim().isEmpty())) {
                name = "患者" + pid;
            }

            if (!byName.isEmpty() && !String.valueOf(name).contains(byName)) {
                continue;
            }

            Map<String, Object> row = new HashMap<>();
            row.put("patientId", pid);
            row.put("patientName", name);
            rows.add(row);
        }
        rows.sort(Comparator.comparingLong(o -> Long.parseLong(String.valueOf(o.get("patientId")))));
        return AjaxResult.success("success", rows);
    }

    @PostMapping("/api/doctor/patient/rehab-plan/generate")
    public AjaxResult doctorGeneratePlan(@RequestBody Map<String, Object> body) {
        Long patientId = toLong(body.get("patientId"));
        if (patientId == null) {
            return AjaxResult.error(400, "patientId 必填");
        }
        return AjaxResult.success("success", aiGatewayService.generateRehabPlan(patientId, "doctor"));
    }

    @PostMapping("/api/doctor/patient/rehab-plan/revise")
    public AjaxResult doctorRevisePlan(@RequestBody Map<String, Object> body) {
        Long patientId = toLong(body.get("patientId"));
        String planId = body.get("planId") == null ? null : String.valueOf(body.get("planId"));
        Object revisedContent = body.get("revisedContent");
        if (patientId == null || planId == null || revisedContent == null) {
            return AjaxResult.error(400, "patientId/planId/revisedContent 必填");
        }

        LoginUser loginUser = getLoginUser();
        String revisedBy = loginUser == null ? "doctor_unknown" : String.valueOf(loginUser.getUserId());
        Object data = aiGatewayService.reviseRehabPlan(patientId, planId, revisedContent, revisedBy);
        return AjaxResult.success("success", data);
    }

    @PostMapping("/api/doctor/patient/rehab-plan/dispatch")
    public AjaxResult doctorDispatchPlan(@RequestBody Map<String, Object> body) {
        Long patientId = toLong(body.get("patientId"));
        String planId = body.get("planId") == null ? null : String.valueOf(body.get("planId"));
        if (patientId == null || planId == null) {
            return AjaxResult.error(400, "patientId/planId 必填");
        }
        Object data = aiGatewayService.dispatchRehabPlanWithTrace(patientId, planId, "doctor");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/doctor/patient/rehab-plan/dispatch/trace")
    public AjaxResult doctorDispatchPlanTrace(@RequestParam("patientId") Long patientId,
                                              @RequestParam("planId") String planId) {
        if (patientId == null || planId == null || planId.trim().isEmpty()) {
            return AjaxResult.error(400, "patientId/planId 必填");
        }
        Map<String, Object> data = aiGatewayService.getRehabDispatchTrace(patientId, planId);
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/doctor/patient/rehab-plan/current")
    public AjaxResult doctorCurrentPlan(@RequestParam("patientId") Long patientId,
                                        @RequestParam(value = "planId", required = false) String planId) {
        Object data = buildDoctorRehabPlanView(patientId, planId);
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/doctor/patient/health-report/daily")
    public AjaxResult doctorHealthReportDaily(@RequestParam("patientId") Long patientId) {
        Object raw = loadMappedLocalDailyReport(patientId, "doctor");
        if (raw == null) {
            return AjaxResult.success("success", buildEmptyHealthReportModule(patientId, "daily"));
        }
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "daily"));
    }

    @GetMapping("/system/health-report/daily")
    public AjaxResult patientHealthReportDaily(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object raw = aiGatewayService.healthReportDaily(resolved, "patient");
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, resolved, "daily"));
    }

    @GetMapping("/api/family/patient/health-report/daily")
    public AjaxResult familyHealthReportDaily(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object raw = aiGatewayService.healthReportDaily(patientId, "family");
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "daily"));
    }

    @GetMapping("/api/doctor/patient/health-report/weekly")
    public AjaxResult doctorHealthReportWeekly(@RequestParam("patientId") Long patientId) {
        Object raw = loadLatestLocalReport(patientId, "doctor", "weekly");
        if (raw == null) {
            return AjaxResult.success("success", buildEmptyHealthReportModule(patientId, "weekly"));
        }
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "weekly"));
    }

    @GetMapping("/system/health-report/weekly")
    public AjaxResult patientHealthReportWeekly(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object raw = loadLatestLocalReport(resolved, "patient", "weekly");
        if (raw == null) {
            raw = aiGatewayService.healthReportWeekly(resolved, "patient");
        }
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, resolved, "weekly"));
    }

    @GetMapping("/api/family/patient/health-report/weekly")
    public AjaxResult familyHealthReportWeekly(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object raw = aiGatewayService.healthReportWeekly(patientId, "family");
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "weekly"));
    }

    @GetMapping("/api/doctor/patient/health-report/monthly")
    public AjaxResult doctorHealthReportMonthly(@RequestParam("patientId") Long patientId) {
        Object raw = loadLatestLocalReport(patientId, "doctor", "monthly");
        if (raw == null) {
            return AjaxResult.success("success", buildEmptyHealthReportModule(patientId, "monthly"));
        }
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "monthly"));
    }

    @GetMapping("/api/doctor/patient/health-report/pdf/view")
    public void doctorHealthReportPdfView(@RequestParam("patientId") Long patientId,
                                          @RequestParam(value = "reportType", required = false, defaultValue = "daily") String reportType,
                                          HttpServletResponse response) throws IOException {
        Map<String, Object> report = buildIndicatorChangePdf(patientId, "doctor", reportType);
        Object pdfObj = report.get("pdf");
        String pdfPath = pdfObj == null ? null : String.valueOf(pdfObj).trim();

        streamPdfFromPath(pdfPath, response);
    }

    private void streamPdfFromPath(String pdfPath, HttpServletResponse response) throws IOException {
        if (pdfPath == null || pdfPath.isEmpty()) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到PDF报告");
            return;
        }

        if (isHttpUrl(pdfPath)) {
            response.sendRedirect(pdfPath);
            return;
        }

        Path pdfFile = Paths.get(pdfPath).normalize();
        if (!Files.exists(pdfFile) || !Files.isRegularFile(pdfFile)) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "PDF文件不存在");
            return;
        }

        if (!pdfFile.getFileName().toString().toLowerCase().endsWith(".pdf")) {
            writeJsonError(response, HttpServletResponse.SC_BAD_REQUEST, "仅支持PDF预览");
            return;
        }

        String encodedFileName = URLEncoder.encode(pdfFile.getFileName().toString(), StandardCharsets.UTF_8.name()).replace("+", "%20");
        response.setContentType("application/pdf");
        response.setHeader("Content-Disposition", "inline; filename*=UTF-8''" + encodedFileName);

        try (InputStream inputStream = Files.newInputStream(pdfFile)) {
            byte[] buffer = new byte[8192];
            int len;
            while ((len = inputStream.read(buffer)) != -1) {
                response.getOutputStream().write(buffer, 0, len);
            }
            response.flushBuffer();
        }
    }

    private void writeJsonError(HttpServletResponse response, int code, String msg) throws IOException {
        response.setStatus(code);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":" + code + ",\"msg\":\"" + msg + "\"}");
    }

    @GetMapping("/system/health-report/monthly")
    public AjaxResult patientHealthReportMonthly(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object raw = loadLatestLocalReport(resolved, "patient", "monthly");
        if (raw == null) {
            raw = aiGatewayService.healthReportMonthly(resolved, "patient");
        }
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, resolved, "monthly"));
    }

    @GetMapping("/api/family/patient/health-report/monthly")
    public AjaxResult familyHealthReportMonthly(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object raw = aiGatewayService.healthReportMonthly(patientId, "family");
        return AjaxResult.success("success", buildHealthReportPdfModule(raw, patientId, "monthly"));
    }

    @GetMapping("/api/doctor/patient/indicator/change")
    public AjaxResult doctorIndicatorChange(@RequestParam("patientId") Long patientId,
                                            @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        return AjaxResult.success("success", buildIndicatorChangePdf(patientId, "doctor", period));
    }

    @GetMapping("/api/doctor/patient/indicator/change/history")
    public AjaxResult doctorIndicatorChangeHistory(@RequestParam("patientId") Long patientId,
                                                   @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        String reportType = normalizeReportType(period);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(patientId, "doctor", reportType)) {
            Map<String, Object> row = buildHealthReportPdfModule(item.report, patientId, reportType);
            row.put("sourceDate", item.sourceDate);
            row.put("displayDate", item.displayDate);
            rows.add(row);
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/api/doctor/patient/indicator/change/history/pdf")
    public void doctorIndicatorHistoryPdfView(@RequestParam("patientId") Long patientId,
                                              @RequestParam("sourceDate") String sourceDate,
                                              @RequestParam(value = "period", required = false, defaultValue = "daily") String period,
                                              HttpServletResponse response) throws IOException {
        String reportType = normalizeReportType(period);
        JSONObject report = loadLocalReportByDate(patientId, "doctor", reportType, sourceDate);
        if (report == null) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到历史报告");
            return;
        }

        Map<String, Object> module = buildHealthReportPdfModule(report, patientId, reportType);
        String pdfPath = module.get("pdf") == null ? null : String.valueOf(module.get("pdf")).trim();
        streamPdfFromPath(pdfPath, response);
    }

    @GetMapping("/system/indicator/change")
    public AjaxResult patientIndicatorChange(@RequestParam(value = "patientId", required = false) Long patientId,
                                             @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        return AjaxResult.success("success", buildIndicatorChangePdf(resolved, "patient", period));
    }

    @GetMapping("/system/indicator/change/history")
    public AjaxResult patientIndicatorChangeHistory(@RequestParam(value = "patientId", required = false) Long patientId,
                                                    @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }

        String reportType = normalizeReportType(period);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(resolved, "patient", reportType)) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildHealthReportPdfModule(item.report, resolved, reportType);
            row.put("sourceDate", item.sourceDate);
            row.put("displayDate", item.displayDate);
            rows.add(row);
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/system/indicator/change/history/pdf")
    public void patientIndicatorHistoryPdfView(@RequestParam(value = "patientId", required = false) Long patientId,
                                               @RequestParam("sourceDate") String sourceDate,
                                               @RequestParam(value = "period", required = false, defaultValue = "daily") String period,
                                               HttpServletResponse response) throws IOException {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            writeJsonError(response, HttpServletResponse.SC_BAD_REQUEST, "patientId 无效");
            return;
        }

        String reportType = normalizeReportType(period);
        if (!isWithinPatientHistoryCutoff(sourceDate)) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到历史报告");
            return;
        }
        JSONObject report = loadLocalReportByDate(resolved, "patient", reportType, sourceDate);
        if (report == null) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到历史报告");
            return;
        }

        Map<String, Object> module = buildHealthReportPdfModule(report, resolved, reportType);
        String pdfPath = module.get("pdf") == null ? null : String.valueOf(module.get("pdf")).trim();
        streamPdfFromPath(pdfPath, response);
    }

    @GetMapping("/api/family/patient/indicator/change")
    public AjaxResult familyIndicatorChange(@RequestParam("patientId") Long patientId,
                                            @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        return AjaxResult.success("success", buildIndicatorChangePdf(patientId, "family", period));
    }

    @GetMapping("/api/family/patient/indicator/change/history")
    public AjaxResult familyIndicatorChangeHistory(@RequestParam("patientId") Long patientId,
                                                   @RequestParam(value = "period", required = false, defaultValue = "daily") String period) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }

        String reportType = normalizeReportType(period);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(patientId, "family", reportType)) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildHealthReportPdfModule(item.report, patientId, reportType);
            row.put("sourceDate", item.sourceDate);
            row.put("displayDate", item.displayDate);
            rows.add(row);
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/api/family/patient/indicator/change/history/pdf")
    public void familyIndicatorHistoryPdfView(@RequestParam("patientId") Long patientId,
                                              @RequestParam("sourceDate") String sourceDate,
                                              @RequestParam(value = "period", required = false, defaultValue = "daily") String period,
                                              HttpServletResponse response) throws IOException {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            writeJsonError(response, HttpServletResponse.SC_FORBIDDEN, "当前患者未绑定或无权限查看");
            return;
        }

        if (!isWithinPatientHistoryCutoff(sourceDate)) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到历史报告");
            return;
        }

        String reportType = normalizeReportType(period);
        JSONObject report = loadLocalReportByDate(patientId, "family", reportType, sourceDate);
        if (report == null) {
            writeJsonError(response, HttpServletResponse.SC_NOT_FOUND, "未找到历史报告");
            return;
        }

        Map<String, Object> module = buildHealthReportPdfModule(report, patientId, reportType);
        String pdfPath = module.get("pdf") == null ? null : String.valueOf(module.get("pdf")).trim();
        streamPdfFromPath(pdfPath, response);
    }

    @GetMapping("/api/patient/rehab-plan/current")
    public AjaxResult patientCurrentPlan(@RequestParam(value = "patientId", required = false) Long patientId,
                                         @RequestParam(value = "planId", required = false) String planId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }
        Object raw = aiGatewayService.viewRehabPlan(resolved, planId, "patient");
        Object data = buildRehabRecommendationModule(raw, resolved, "patient");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/patient/rehab-plan/history")
    public AjaxResult patientRehabPlanHistory(@RequestParam(value = "patientId", required = false) Long patientId) {
        Long resolved = resolvePatientIdOrCurrent(patientId);
        if (resolved == null) {
            return AjaxResult.error(400, "patientId 无效");
        }

        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(resolved, "patient", "daily")) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildRehabHistoryItemFromReport(item, resolved);
            if (!row.isEmpty()) {
                rows.add(row);
            }
        }

        // 截止日优先展示医生修改并已下发的方案，确保患者端看到最新下发内容。
        try {
            Object currentRaw = aiGatewayService.viewRehabPlan(resolved, null, "patient");
            Map<String, Object> currentModule = buildRehabRecommendationModule(currentRaw, resolved, "patient");
            @SuppressWarnings("unchecked")
            List<String> revised = currentModule.get("doctorRevisedRecommendations") instanceof List
                ? (List<String>) currentModule.get("doctorRevisedRecommendations")
                : new ArrayList<String>();
            @SuppressWarnings("unchecked")
            List<String> ai = currentModule.get("aiRecommendations") instanceof List
                ? (List<String>) currentModule.get("aiRecommendations")
                : new ArrayList<String>();

            List<String> selected = (revised != null && !revised.isEmpty()) ? revised : ai;
            if (selected != null && !selected.isEmpty()) {
                String cutoffSourceDate = resolvePatientHistorySourceCutoffDate();
                String cutoffDisplayDate = mapSourceDateToDisplayDate(cutoffSourceDate);

                JSONObject currentObj = toJsonObject(currentRaw);
                String planId = currentObj.getString("planId");
                Object version = currentObj.get("version");

                Map<String, Object> target = null;
                for (Map<String, Object> row : rows) {
                    if (cutoffSourceDate.equals(String.valueOf(row.get("sourceDate")))) {
                        target = row;
                        break;
                    }
                }

                if (target == null) {
                    target = new HashMap<>();
                    target.put("id", cutoffSourceDate + "_rehab");
                    target.put("patientId", String.valueOf(resolved));
                    target.put("sourceDate", cutoffSourceDate);
                    target.put("displayDate", cutoffDisplayDate);
                    target.put("planId", planId == null ? ("RP_" + resolved + "_" + cutoffSourceDate.replace("-", "")) : planId);
                    target.put("version", version == null ? 1 : version);
                    rows.add(target);
                }

                target.put("status", "dispatched_revised");
                target.put("recommendationSource", revised != null && !revised.isEmpty() ? "doctor_revised" : "ai_plan");
                target.put("recommendations", selected);
                target.put("aiRecommendations", ai == null ? new ArrayList<String>() : ai);
                target.put("doctorRevisedRecommendations", revised == null ? new ArrayList<String>() : revised);
            }
        } catch (Exception ex) {
            log.warn("[PATIENT_REHAB_HISTORY_MERGE_SKIP] patientId={}, err={}", resolved, ex.getMessage());
        }

        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    @GetMapping("/api/family/patient/rehab-plan/current")
    public AjaxResult familyCurrentPlan(@RequestParam("patientId") Long patientId,
                                        @RequestParam(value = "planId", required = false) String planId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }
        Object raw = aiGatewayService.viewRehabPlan(patientId, planId, "family");
        Object data = buildRehabRecommendationModule(raw, patientId, "family");
        return AjaxResult.success("success", data);
    }

    @GetMapping("/api/family/patient/rehab-plan/history")
    public AjaxResult familyRehabPlanHistory(@RequestParam("patientId") Long patientId) {
        Long familyId = getLoginUser().getUserId();
        if (!sysPatientFamilyService.isBound(familyId, patientId)) {
            return AjaxResult.error(403, "当前患者未绑定或无权限查看");
        }

        List<Map<String, Object>> rows = new ArrayList<>();
        for (ReportHistoryItem item : loadLocalReportHistory(patientId, "family", "daily")) {
            if (!isWithinPatientHistoryCutoff(item.sourceDate)) {
                continue;
            }
            Map<String, Object> row = buildRehabHistoryItemFromReport(item, patientId);
            if (!row.isEmpty()) {
                rows.add(row);
            }
        }
        rows.sort((a, b) -> String.valueOf(b.get("sourceDate")).compareTo(String.valueOf(a.get("sourceDate"))));
        return AjaxResult.success("success", rows);
    }

    private Long resolvePatientIdOrCurrent(Long patientId) {
        if (patientId != null) {
            return patientId;
        }
        LoginUser loginUser = getLoginUser();
        return loginUser == null ? null : loginUser.getUserId();
    }

    private Long toLong(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return Long.valueOf(String.valueOf(value));
        } catch (Exception e) {
            return null;
        }
    }

    private List<Map<String, Object>> buildIndicatorMetrics(Recovery latest, Recovery previous) {
        List<Map<String, Object>> metrics = new ArrayList<>();
        metrics.add(metricItem("ntProbnp", "NT_proBNP", latest.getNtProbnp(), previous == null ? null : previous.getNtProbnp(), false));
        metrics.add(metricItem("lvef", "LVEF", latest.getLVEF(), previous == null ? null : previous.getLVEF(), true));
        metrics.add(metricItem("cpet1", "峰值公斤摄氧量", latest.getCPET1(), previous == null ? null : previous.getCPET1(), true));
        metrics.add(metricItem("cpet2", "无氧公斤摄氧量", latest.getCPET2(), previous == null ? null : previous.getCPET2(), true));
        metrics.add(metricItem("peakBloodPressure", "峰值血压", latest.getPeakBloodPressure(), previous == null ? null : previous.getPeakBloodPressure(), false));
        metrics.add(metricItem("peakHeartRate", "峰值心率", latest.getPeakHeartRate(), previous == null ? null : previous.getPeakHeartRate(), false));
        metrics.add(metricItem("anaerobicThresholdBloodPressure", "无氧阈血压", latest.getAnaerobicThresholdBloodPressure(), previous == null ? null : previous.getAnaerobicThresholdBloodPressure(), false));
        metrics.add(metricItem("anaerobicThresholdHeartRate", "无氧阈心率", latest.getAnaerobicThresholdHeartRate(), previous == null ? null : previous.getAnaerobicThresholdHeartRate(), false));
        return metrics;
    }

    private Map<String, Object> buildRiskModule(Object raw, Long patientId) {
        JSONObject obj = toJsonObject(raw);
        Map<String, Object> data = new HashMap<>();
        data.put("patientId", String.valueOf(patientId));
        data.put("riskLevel", obj.getString("riskLevel"));
        data.put("heartRateDistribution", obj.get("heartRateDistribution"));
        data.put("warningDistribution", obj.get("warningDistribution"));
        data.put("description", obj.getString("description"));
        return data;
    }

    private Map<String, Object> buildRiskHistoryItemFromReport(ReportHistoryItem item, Long patientId) {
        JSONObject report = item.report;
        if (report == null) {
            return Collections.emptyMap();
        }

        JSONObject moduleOutputs = report.getJSONObject("module_outputs");
        JSONObject riskPrediction = moduleOutputs == null ? null : moduleOutputs.getJSONObject("risk_prediction");
        JSONObject assessment = report.getJSONObject("clinical_assessment");

        String riskLevel = riskPrediction == null ? null : riskPrediction.getString("riskLevel");
        if (riskLevel == null || riskLevel.trim().isEmpty()) {
            riskLevel = assessment == null ? null : assessment.getString("risk_level");
        }
        if (riskLevel == null || riskLevel.trim().isEmpty()) {
            riskLevel = report.getString("riskLevel");
        }
        if (riskLevel == null || riskLevel.trim().isEmpty()) {
            riskLevel = "未知";
        }

        String description = riskPrediction == null ? null : riskPrediction.getString("description");
        if (description == null || description.trim().isEmpty()) {
            description = assessment == null ? null : assessment.getString("condition_status");
        }
        if (description == null || description.trim().isEmpty()) {
            JSONObject hr = report.getJSONObject("data_analysis") == null ? null : report.getJSONObject("data_analysis").getJSONObject("heart_rate");
            description = hr == null ? "-" : hr.getString("analysis");
        }
        if (looksMojibake(description)) {
            description = "风险评估已生成，请持续监测心率变化。";
        }

        Map<String, Object> hrSummary = new HashMap<>();
        if (riskPrediction != null && riskPrediction.getJSONObject("heartRateDistribution") != null) {
            hrSummary.putAll(toMap(riskPrediction.getJSONObject("heartRateDistribution")));
        } else {
            JSONObject dataAnalysis = report.getJSONObject("data_analysis");
            JSONObject hr = dataAnalysis == null ? null : dataAnalysis.getJSONObject("heart_rate");
            if (hr != null) {
                hrSummary.put("mean", hr.get("mean"));
                hrSummary.put("min", hr.get("min"));
                hrSummary.put("max", hr.get("max"));
            }
        }

        Map<String, Object> warningSummary = new HashMap<>();
        if (riskPrediction != null && riskPrediction.getJSONObject("warningDistribution") != null) {
            warningSummary.putAll(toMap(riskPrediction.getJSONObject("warningDistribution")));
        }
        if (warningSummary.isEmpty()) {
            warningSummary.put(String.valueOf(riskLevel), "100%");
        }

        Map<String, Object> row = new HashMap<>();
        row.put("id", item.sourceDate + "_risk");
        row.put("patientId", String.valueOf(patientId));
        row.put("sourceDate", item.sourceDate);
        row.put("displayDate", item.displayDate);
        row.put("riskLevel", riskLevel);
        row.put("heartRateDistribution", hrSummary);
        row.put("warningDistribution", warningSummary);
        row.put("description", description == null ? "-" : description);
        return row;
    }

    private Map<String, Object> buildEmptyRiskModule(Long patientId) {
        Map<String, Object> row = new HashMap<>();
        row.put("id", "risk_empty_" + patientId);
        row.put("patientId", String.valueOf(patientId));
        row.put("riskLevel", "low");
        row.put("heartRateDistribution", new HashMap<String, Object>());
        row.put("warningDistribution", new HashMap<String, Object>());
        row.put("description", "暂无可用风险数据");
        return row;
    }

    private Map<String, Object> buildRehabHistoryItemFromReport(ReportHistoryItem item, Long patientId) {
        JSONObject report = item.report;
        if (report == null) {
            return Collections.emptyMap();
        }

        List<String> recommendations = extractRecommendationTexts(report);
        if (recommendations.isEmpty()) {
            recommendations = extractTopLevelRecommendationTexts(report);
        }

        String compactDate = item.sourceDate == null ? "" : item.sourceDate.replace("-", "");
        String planId = "RP_" + patientId + "_" + compactDate;

        Map<String, Object> row = new HashMap<>();
        row.put("id", item.sourceDate + "_rehab");
        row.put("patientId", String.valueOf(patientId));
        row.put("sourceDate", item.sourceDate);
        row.put("displayDate", item.displayDate);
        row.put("planId", planId);
        row.put("version", 1);
        row.put("status", "mapped_history");
        row.put("recommendationSource", "report");
        row.put("sourcePlanId", planId);
        row.put("sourceVersion", 1);
        row.put("recommendations", recommendations);
        row.put("aiRecommendations", recommendations);
        row.put("doctorRevisedRecommendations", new ArrayList<String>());
        return row;
    }

    private Map<String, Object> buildHealthReportPdfModule(Object raw, Long patientId, String reportType) {
        JSONObject obj = toJsonObject(raw);
        JSONObject artifacts = obj.getJSONObject("artifacts");
        Map<String, Object> data = new HashMap<>();
        data.put("patientId", String.valueOf(patientId));
        data.put("reportType", reportType);
        data.put("pdf", resolvePdfPath(obj, artifacts));
        data.put("reportDate", resolveReportDate(obj, reportType));
        data.put("recommendations", extractRecommendationTexts(obj));
        return data;
    }

    private Map<String, Object> buildEmptyHealthReportModule(Long patientId, String reportType) {
        Map<String, Object> data = new HashMap<>();
        data.put("patientId", String.valueOf(patientId));
        data.put("reportType", reportType);
        data.put("pdf", null);
        data.put("reportDate", null);
        data.put("recommendations", new ArrayList<String>());
        return data;
    }

    private Map<String, Object> buildDoctorRehabPlanView(Long patientId, String planId) {
        JSONObject plan = new JSONObject();
        try {
            plan = toJsonObject(aiGatewayService.viewRehabPlan(patientId, planId, "doctor"));
        } catch (Exception ignored) {
            // 方案视图服务超时时，返回可用的本地报告recommendations，避免医生端加载失败。
        }
        JSONObject report = new JSONObject();
        Object local = loadMappedLocalDailyReport(patientId, "doctor");
        if (local != null) {
            report = toJsonObject(local);
        }
        // 医生端按约定使用报告根节点 recommendations（对应报告JSON顶层 recommendations）。
        List<String> reportRecommendations = extractTopLevelRecommendationTexts(report);
        List<String> clinicalRecommendations = extractClinicalRecommendationTexts(report);
        List<String> planRecommendations = extractPlanRecommendationTexts(plan);
        List<String> recommendations = reportRecommendations;
        String recommendationSource = reportRecommendations.isEmpty() ? "report_unavailable" : "report";

        String selectedFirst = recommendations.isEmpty() ? "" : recommendations.get(0);
        String reportFirst = reportRecommendations.isEmpty() ? "" : reportRecommendations.get(0);
        String clinicalFirst = clinicalRecommendations.isEmpty() ? "" : clinicalRecommendations.get(0);
        log.info("[REHAB_RECO_VERIFY] patientId={}, source={}, selectedCount={}, reportTopCount={}, clinicalCount={}, selectedFirst={}, reportFirst={}, clinicalFirst={}",
            patientId,
            recommendationSource,
            recommendations.size(),
            reportRecommendations.size(),
            clinicalRecommendations.size(),
            selectedFirst,
            reportFirst,
            clinicalFirst);

        plan.put("recommendations", recommendations);
        plan.put("recommendationsText", String.join("\n", recommendations));
        plan.put("aiRecommendations", recommendations);
        plan.put("doctorRevisedRecommendations", new ArrayList<String>());
        plan.put("reportRecommendations", reportRecommendations);
        plan.put("planRecommendations", planRecommendations);
        plan.put("recommendationSource", recommendationSource);
        plan.put("reportType", "daily");

        JSONObject artifacts = report.getJSONObject("artifacts");
        if (artifacts != null) {
            plan.put("doctorReportJson", artifacts.getString("json"));
            plan.put("doctorReportPdf", resolvePdfPath(report, artifacts));
        }
        return toMap(plan);
    }

    private List<String> extractPlanRecommendationTexts(JSONObject plan) {
        LinkedHashSet<String> texts = new LinkedHashSet<>();
        collectRecommendations(plan.get("doctorRevisedPlan"), texts);
        collectRecommendations(plan.get("aiPlan"), texts);
        collectRecommendations(plan, texts);
        return new ArrayList<>(texts);
    }

    private String resolvePdfPath(JSONObject obj, JSONObject artifacts) {
        if (artifacts != null) {
            String fromArtifacts = artifacts.getString("pdf");
            if (fromArtifacts != null && !fromArtifacts.trim().isEmpty()) {
                return fromArtifacts;
            }

            JSONObject moduleFiles = artifacts.getJSONObject("module_files");
            if (moduleFiles != null) {
                String fromModuleFiles = moduleFiles.getString("pdf");
                if (fromModuleFiles != null && !fromModuleFiles.trim().isEmpty()) {
                    return fromModuleFiles;
                }
            }
        }

        String direct = obj.getString("pdf");
        if (direct != null && !direct.trim().isEmpty()) {
            return direct;
        }
        return null;
    }

    private String resolveReportDate(JSONObject obj, String reportType) {
        if ("weekly".equals(reportType)) {
            String ws = obj.getString("week_start");
            String we = obj.getString("week_end");
            if (ws != null && we != null) {
                return ws + " ~ " + we;
            }
        }
        if ("monthly".equals(reportType)) {
            String month = obj.getString("month");
            if (month != null && !month.trim().isEmpty()) {
                return month;
            }
        }
        String date = obj.getString("date");
        if (date != null && !date.trim().isEmpty()) {
            return date;
        }
        return null;
    }

    private List<String> extractRecommendationTexts(JSONObject obj) {
        List<String> result = new ArrayList<>();

        Object top = obj.get("recommendations");
        if (top instanceof List) {
            for (Object item : (List<?>) top) {
                if (item != null) {
                    String text = String.valueOf(item).trim();
                    if (!text.isEmpty() && !result.contains(text)) {
                        result.add(text);
                    }
                }
            }
        }

        JSONObject assessment = obj.getJSONObject("clinical_assessment");
        if (assessment != null) {
            Object nested = assessment.get("recommendations");
            if (nested instanceof List) {
                for (Object item : (List<?>) nested) {
                    if (item != null) {
                        String text = String.valueOf(item).trim();
                        if (!text.isEmpty() && !result.contains(text)) {
                            result.add(text);
                        }
                    }
                }
            }
        }
        return result;
    }

    private List<String> extractTopLevelRecommendationTexts(JSONObject obj) {
        List<String> result = new ArrayList<>();
        if (obj == null) {
            return result;
        }

        Object top = obj.get("recommendations");
        if (top instanceof List) {
            for (Object item : (List<?>) top) {
                if (item != null) {
                    String text = String.valueOf(item).trim();
                    if (!text.isEmpty() && !result.contains(text)) {
                        result.add(text);
                    }
                }
            }
        }
        return result;
    }

    private List<String> extractClinicalRecommendationTexts(JSONObject obj) {
        List<String> result = new ArrayList<>();
        if (obj == null) {
            return result;
        }

        JSONObject assessment = obj.getJSONObject("clinical_assessment");
        if (assessment == null) {
            return result;
        }

        Object nested = assessment.get("recommendations");
        if (!(nested instanceof List)) {
            return result;
        }

        for (Object item : (List<?>) nested) {
            if (item != null) {
                String text = String.valueOf(item).trim();
                if (!text.isEmpty() && !result.contains(text)) {
                    result.add(text);
                }
            }
        }
        return result;
    }

    private JSONObject loadLatestLocalReport(Long patientId, String scene, String reportType) {
        try {
            String agentId = toAgentId(patientId);
            String endDir = toEndDir(scene);
            Path baseDir = Paths.get(reportRoot, agentId, endDir, reportType).normalize();
            if (!Files.exists(baseDir) || !Files.isDirectory(baseDir)) {
                return null;
            }

            Path latestDir = null;
            long latestTime = Long.MIN_VALUE;
            try (java.util.stream.Stream<Path> stream = Files.list(baseDir)) {
                for (Path p : (Iterable<Path>) stream::iterator) {
                    if (!Files.isDirectory(p)) {
                        continue;
                    }
                    long ts = Files.getLastModifiedTime(p).toMillis();
                    if (ts > latestTime) {
                        latestTime = ts;
                        latestDir = p;
                    }
                }
            }
            if (latestDir == null) {
                return null;
            }

            Path jsonPath = null;
            String jsonSuffix = "_" + endDir + ".json";
            try (java.util.stream.Stream<Path> stream = Files.list(latestDir)) {
                for (Path p : (Iterable<Path>) stream::iterator) {
                    String name = p.getFileName().toString();
                    if (Files.isRegularFile(p) && name.endsWith(jsonSuffix)) {
                        jsonPath = p;
                        break;
                    }
                }
            }
            if (jsonPath == null || !Files.exists(jsonPath)) {
                return null;
            }

            String text = new String(Files.readAllBytes(jsonPath), StandardCharsets.UTF_8);
            return JSONObject.parseObject(text);
        } catch (Exception e) {
            return null;
        }
    }

    private static class ReportHistoryItem {
        private final String sourceDate;
        private final String displayDate;
        private final JSONObject report;

        private ReportHistoryItem(String sourceDate, String displayDate, JSONObject report) {
            this.sourceDate = sourceDate;
            this.displayDate = displayDate;
            this.report = report;
        }
    }

    private List<ReportHistoryItem> loadLocalReportHistory(Long patientId, String scene, String reportType) {
        List<ReportHistoryItem> rows = new ArrayList<>();
        try {
            String agentId = toAgentId(patientId);
            String endDir = toEndDir(scene);
            Path baseDir = Paths.get(reportRoot, agentId, endDir, reportType).normalize();
            if (!Files.exists(baseDir) || !Files.isDirectory(baseDir)) {
                return rows;
            }

            List<Path> dateDirs = new ArrayList<>();
            try (java.util.stream.Stream<Path> stream = Files.list(baseDir)) {
                for (Path p : (Iterable<Path>) stream::iterator) {
                    if (Files.isDirectory(p)) {
                        dateDirs.add(p);
                    }
                }
            }
            dateDirs.sort(Comparator.comparing(p -> p.getFileName().toString()));

            String jsonSuffix = "_" + endDir + ".json";
            for (Path dir : dateDirs) {
                String sourceDate = dir.getFileName().toString();
                if ("daily".equals(reportType) && !isSourceDateInRange(sourceDate)) {
                    continue;
                }
                Path jsonPath = null;
                try (java.util.stream.Stream<Path> stream = Files.list(dir)) {
                    for (Path p : (Iterable<Path>) stream::iterator) {
                        if (Files.isRegularFile(p) && p.getFileName().toString().endsWith(jsonSuffix)) {
                            jsonPath = p;
                            break;
                        }
                    }
                }
                if (jsonPath == null || !Files.exists(jsonPath)) {
                    continue;
                }

                String text = new String(Files.readAllBytes(jsonPath), StandardCharsets.UTF_8);
                JSONObject report = JSONObject.parseObject(text);
                String displayDate = mapSourceDateToDisplayDate(sourceDate);
                rows.add(new ReportHistoryItem(sourceDate, displayDate, report));
            }
        } catch (Exception e) {
            return rows;
        }
        return rows;
    }

    private String mapSourceDateToDisplayDate(String sourceDate) {
        try {
            LocalDate source = LocalDate.parse(sourceDate, DateTimeFormatter.ISO_LOCAL_DATE);
            long offset = ChronoUnit.DAYS.between(SOURCE_BASE_DATE, source);
            return DISPLAY_BASE_DATE.plusDays(offset).toString();
        } catch (Exception e) {
            return sourceDate;
        }
    }

    private boolean isSourceDateInRange(String sourceDate) {
        try {
            LocalDate source = LocalDate.parse(sourceDate, DateTimeFormatter.ISO_LOCAL_DATE);
            return !source.isBefore(SOURCE_BASE_DATE) && !source.isAfter(SOURCE_END_DATE);
        } catch (Exception e) {
            return false;
        }
    }

    private JSONObject loadLocalReportByDate(Long patientId, String scene, String reportType, String dateLabel) {
        try {
            if (dateLabel == null || dateLabel.trim().isEmpty()) {
                return null;
            }
            String agentId = toAgentId(patientId);
            String endDir = toEndDir(scene);
            Path dateDir = Paths.get(reportRoot, agentId, endDir, reportType, dateLabel.trim()).normalize();
            if (!Files.exists(dateDir) || !Files.isDirectory(dateDir)) {
                return null;
            }

            String jsonName = dateLabel.trim() + "_" + endDir + ".json";
            Path jsonPath = dateDir.resolve(jsonName);
            if (!Files.exists(jsonPath) || !Files.isRegularFile(jsonPath)) {
                return null;
            }

            String text = new String(Files.readAllBytes(jsonPath), StandardCharsets.UTF_8);
            return JSONObject.parseObject(text);
        } catch (Exception e) {
            return null;
        }
    }

    private JSONObject loadMappedLocalDailyReport(Long patientId, String scene) {
        String mappedDate = resolveMappedDailySourceDate(LocalDate.now());
        JSONObject mapped = loadLocalReportByDate(patientId, scene, "daily", mappedDate);
        if (mapped == null) {
            log.warn("[REPORT_MAP_MISS] patientId={}, scene={}, mappedDate={} not found", patientId, scene, mappedDate);
        }
        return mapped;
    }

    private String resolveMappedDailySourceDate(LocalDate displayDate) {
        if (displayDate == null) {
            return SOURCE_BASE_DATE.toString();
        }

        long offset = ChronoUnit.DAYS.between(DISPLAY_BASE_DATE, displayDate);
        if (offset < 0) {
            offset = 0;
        }

        long maxOffset = ChronoUnit.DAYS.between(SOURCE_BASE_DATE, SOURCE_END_DATE);
        if (offset > maxOffset) {
            offset = maxOffset;
        }

        return SOURCE_BASE_DATE.plusDays(offset).toString();
    }

    private String resolvePatientHistorySourceCutoffDate() {
        return resolveMappedDailySourceDate(LocalDate.now());
    }

    private boolean isWithinPatientHistoryCutoff(String sourceDate) {
        if (sourceDate == null || sourceDate.trim().isEmpty()) {
            return false;
        }
        try {
            LocalDate source = LocalDate.parse(sourceDate, DateTimeFormatter.ISO_LOCAL_DATE);
            LocalDate cutoff = LocalDate.parse(resolvePatientHistorySourceCutoffDate(), DateTimeFormatter.ISO_LOCAL_DATE);
            return !source.isAfter(cutoff);
        } catch (Exception e) {
            return false;
        }
    }

    private String toAgentId(Long patientId) {
        if (patientId == null) {
            return "";
        }
        if (patientId == 10L) {
            return "P_001";
        }
        if (patientId == 11L) {
            return "P_002";
        }
        if (patientId == 12L) {
            return "P_003";
        }
        return String.valueOf(patientId);
    }

    private List<Long> resolveDoctorMappedPatientsByDate(String sourceDate) {
        List<Long> ids = new ArrayList<>();
        List<Long> knownIds = new ArrayList<>();
        knownIds.add(10L);
        knownIds.add(11L);
        knownIds.add(12L);

        for (Long id : knownIds) {
            JSONObject report = loadLocalReportByDate(id, "doctor", "daily", sourceDate);
            if (report != null) {
                ids.add(id);
            }
        }
        return ids;
    }

    private String toEndDir(String scene) {
        if ("doctor".equalsIgnoreCase(scene)) {
            return "doctor_end";
        }
        if ("family".equalsIgnoreCase(scene)) {
            return "family_end";
        }
        return "patient_end";
    }

    private Map<String, Object> toMap(JSONObject obj) {
        Map<String, Object> map = new HashMap<>();
        for (String key : obj.keySet()) {
            map.put(key, obj.get(key));
        }
        return map;
    }

    private Map<String, Object> buildIndicatorChangePdf(Long patientId, String scene, String period) {
        String reportType = normalizeReportType(period);
        Object raw;
        if ("doctor".equalsIgnoreCase(scene)) {
            if ("daily".equals(reportType)) {
                raw = loadMappedLocalDailyReport(patientId, scene);
            } else {
                raw = loadLatestLocalReport(patientId, scene, reportType);
            }
            if (raw == null) {
                return buildEmptyHealthReportModule(patientId, reportType);
            }
        } else if ("weekly".equals(reportType)) {
            raw = aiGatewayService.healthReportWeekly(patientId, scene);
        } else if ("monthly".equals(reportType)) {
            raw = aiGatewayService.healthReportMonthly(patientId, scene);
        } else {
            raw = aiGatewayService.healthReportDaily(patientId, scene);
        }
        return buildHealthReportPdfModule(raw, patientId, reportType);
    }

    private boolean isKnownAiPatient(Long patientId) {
        return patientId != null && (patientId == 10L || patientId == 11L || patientId == 12L);
    }

    private boolean isHttpUrl(String path) {
        if (path == null) {
            return false;
        }
        String lower = path.toLowerCase();
        return lower.startsWith("http://") || lower.startsWith("https://");
    }

    private boolean looksMojibake(String text) {
        if (text == null || text.trim().isEmpty()) {
            return false;
        }
        return text.contains("å") || text.contains("Ã") || text.contains("æ") || text.contains("ï¼");
    }

    private Map<String, Object> buildRehabRecommendationModule(Object raw, Long patientId, String scene) {
        JSONObject obj = toJsonObject(raw);
        Set<String> aiRecommendations = new LinkedHashSet<>();
        Set<String> revisedRecommendations = new LinkedHashSet<>();

        collectRecommendations(obj.get("aiPlan"), aiRecommendations);

        JSONObject revised = obj.getJSONObject("doctorRevisedPlan");
        if (revised != null) {
            collectRecommendations(revised.get("content"), revisedRecommendations);
            collectRecommendations(revised, revisedRecommendations);
        }

        String planId = obj.getString("planId");
        Object version = obj.get("version");
        String status = obj.getString("status");

        Map<String, Object> dispatchInfo = new HashMap<>();
        Object directDispatch = obj.get("dispatchInfo");
        if (directDispatch instanceof Map) {
            Map<?, ?> sourceMap = (Map<?, ?>) directDispatch;
            for (Map.Entry<?, ?> entry : sourceMap.entrySet()) {
                if (entry.getKey() != null) {
                    dispatchInfo.put(String.valueOf(entry.getKey()), entry.getValue());
                }
            }
        }

        if ((dispatchInfo.isEmpty()) && planId != null && !planId.trim().isEmpty()) {
            dispatchInfo.putAll(aiGatewayService.getRehabDispatchTrace(patientId, planId));
        }

        if (!dispatchInfo.containsKey("sourcePlanId")) {
            dispatchInfo.put("sourcePlanId", planId);
        }
        if (!dispatchInfo.containsKey("sourceVersion")) {
            dispatchInfo.put("sourceVersion", version);
        }
        if (!dispatchInfo.containsKey("dispatchedPlanId")) {
            dispatchInfo.put("dispatchedPlanId", planId);
        }
        if (!dispatchInfo.containsKey("dispatchedVersion")) {
            dispatchInfo.put("dispatchedVersion", version);
        }

        Map<String, Object> data = new HashMap<>();
        data.put("patientId", String.valueOf(patientId));
        data.put("scene", scene);
        data.put("planId", planId);
        data.put("version", version);
        data.put("status", status);
        data.put("dispatchInfo", dispatchInfo);
        data.put("aiRecommendations", new ArrayList<>(aiRecommendations));
        data.put("doctorRevisedRecommendations", new ArrayList<>(revisedRecommendations));
        data.put("hasDoctorRevision", revised != null && !revisedRecommendations.isEmpty());
        return data;
    }

    private void collectRecommendations(Object node, Set<String> sink) {
        if (node == null) {
            return;
        }
        if (node instanceof JSONObject) {
            JSONObject obj = (JSONObject) node;
            Object direct = obj.get("recommendations");
            if (direct instanceof List) {
                for (Object item : (List<?>) direct) {
                    if (item != null) {
                        String text = String.valueOf(item).trim();
                        if (!text.isEmpty()) {
                            sink.add(text);
                        }
                    }
                }
            }
            for (String key : obj.keySet()) {
                collectRecommendations(obj.get(key), sink);
            }
            return;
        }
        if (node instanceof Map) {
            Map<?, ?> map = (Map<?, ?>) node;
            Object direct = map.get("recommendations");
            if (direct instanceof List) {
                for (Object item : (List<?>) direct) {
                    if (item != null) {
                        String text = String.valueOf(item).trim();
                        if (!text.isEmpty()) {
                            sink.add(text);
                        }
                    }
                }
            }
            for (Object value : map.values()) {
                collectRecommendations(value, sink);
            }
            return;
        }
        if (node instanceof List) {
            for (Object item : (List<?>) node) {
                collectRecommendations(item, sink);
            }
        }
    }

    private JSONObject toJsonObject(Object raw) {
        if (raw instanceof JSONObject) {
            return (JSONObject) raw;
        }
        if (raw == null) {
            return new JSONObject();
        }
        return JSONObject.parseObject(JSONObject.toJSONString(raw));
    }

    private String normalizeReportType(String period) {
        if (period == null) {
            return "daily";
        }
        String text = period.trim().toLowerCase();
        if ("weekly".equals(text) || "week".equals(text)) {
            return "weekly";
        }
        if ("monthly".equals(text) || "month".equals(text)) {
            return "monthly";
        }
        return "daily";
    }

    private Map<String, Object> metricItem(String key, String label, Long latest, Long previous, boolean higherIsBetter) {
        Map<String, Object> item = new HashMap<>();
        item.put("key", key);
        item.put("label", label);
        item.put("latest", latest);
        item.put("previous", previous);

        if (latest == null || previous == null) {
            item.put("delta", null);
            item.put("trend", "unknown");
            item.put("status", "insufficient");
            return item;
        }

        long delta = latest - previous;
        item.put("delta", delta);
        if (delta == 0) {
            item.put("trend", "stable");
            item.put("status", "stable");
            return item;
        }

        boolean up = delta > 0;
        item.put("trend", up ? "up" : "down");
        boolean better = (up && higherIsBetter) || (!up && !higherIsBetter);
        item.put("status", better ? "better" : "worse");
        return item;
    }
}
