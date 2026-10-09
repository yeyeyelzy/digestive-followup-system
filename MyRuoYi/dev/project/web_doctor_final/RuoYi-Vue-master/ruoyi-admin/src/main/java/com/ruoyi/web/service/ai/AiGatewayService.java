package com.ruoyi.web.service.ai;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.concurrent.ConcurrentHashMap;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

@Service
public class AiGatewayService {

    private final Map<String, Map<String, Object>> rehabDispatchTraceStore = new ConcurrentHashMap<>();
    private final Map<String, CacheEntry> responseCache = new ConcurrentHashMap<>();

    @Value("${ai.service.base-url}")
    private String baseUrl;

    @Value("${ai.service.timeout-ms}")
    private int timeoutMs;

    @Value("${ai.service.rehab-timeout-ms}")
    private int rehabTimeoutMs;

    @Value("${ai.service.rehab-view-timeout-ms}")
    private int rehabViewTimeoutMs;

    @Value("${ai.service.report-timeout-ms}")
    private int reportTimeoutMs;

    @Value("${ai.service.cache.ttl-ms}")
    private long cacheTtlMs;

    private static class CacheEntry {
        private final Object data;
        private final long expireAt;

        private CacheEntry(Object data, long expireAt) {
            this.data = data;
            this.expireAt = expireAt;
        }

        private boolean isExpired(long now) {
            return now >= expireAt;
        }
    }

    public Object heartTwinRealtime(Long patientId, String scene) {
        Map<String, Object> req = baseReq(patientId, scene);
        return post("/ai/heart-twin/realtime", req);
    }

    public Object heartTwinForecast(Long patientId, String scene) {
        Map<String, Object> req = baseReq(patientId, scene);
        return post("/ai/heart-twin/forecast", req);
    }

    public Object riskPredict(Long patientId, String scene) {
        Map<String, Object> req = baseReq(patientId, scene);
        return post("/ai/risk/predict", req);
    }

    public JSONObject healthyLifeDecision(Long patientId, String date, Map<String, Object> inputs) {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", String.valueOf(patientId));
        req.put("date", date);
        req.put("inputs", inputs == null ? new HashMap<String, Object>() : inputs);
        Object data = post("/ai/recovery/healthy-life-decision", req);
        if (data instanceof JSONObject) {
            return (JSONObject) data;
        }
        return JSON.parseObject(JSON.toJSONString(data));
    }

    public Object generateRehabPlan(Long patientId, String scene) {
        Object data = post("/ai/rehab/plan/generate", baseReq(patientId, scene), rehabTimeoutMs);
        evictPatientCache(patientId);
        return data;
    }

    public Object reviseRehabPlan(Long patientId, String planId, Object revisedContent, String revisedBy) {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", String.valueOf(patientId));
        req.put("planId", planId);
        req.put("revisedContent", revisedContent);
        req.put("revisedBy", revisedBy);
        Object data = post("/ai/rehab/plan/revise", req, rehabTimeoutMs);
        evictPatientCache(patientId);
        return data;
    }

    public Object viewRehabPlan(Long patientId, String planId, String scene) {
        Map<String, Object> req = baseReq(patientId, scene);
        if (planId != null && !planId.trim().isEmpty()) {
            req.put("planId", planId.trim());
        }
        String key = "rehab:view:" + patientId + ":" + normalizeScene(scene) + ":" + normalizePlanId(planId);
        return getOrLoadCache(key, () -> post("/ai/rehab/plan/view", req, rehabViewTimeoutMs));
    }

    public Object dispatchRehabPlan(Long patientId, String planId, String scene) {
        Map<String, Object> req = baseReq(patientId, scene);
        req.put("planId", planId);
        Object data = post("/ai/rehab/plan/dispatch", req, rehabTimeoutMs);
        evictPatientCache(patientId);
        return data;
    }

    public Map<String, Object> dispatchRehabPlanWithTrace(Long patientId, String planId, String scene) {
        JSONObject before = toJsonObject(viewRehabPlan(patientId, planId, scene));
        JSONObject dispatched = toJsonObject(dispatchRehabPlan(patientId, planId, scene));

        String sourcePlanId = stringValue(before.get("planId"), planId);
        Object sourceVersion = before.get("version");
        String dispatchedPlanId = stringValue(dispatched.get("planId"), planId);
        Object dispatchedVersion = dispatched.get("version");

        Map<String, Object> trace = new HashMap<>();
        trace.put("patientId", String.valueOf(patientId));
        trace.put("sourcePlanId", sourcePlanId);
        trace.put("sourceVersion", sourceVersion);
        trace.put("dispatchedPlanId", dispatchedPlanId);
        trace.put("dispatchedVersion", dispatchedVersion);
        trace.put("dispatchScene", (scene == null || scene.trim().isEmpty()) ? "doctor" : scene);
        trace.put("dispatchTime", LocalDateTime.now().toString());

        dispatched.put("dispatchInfo", trace);
        rehabDispatchTraceStore.put(buildTraceKey(patientId, dispatchedPlanId), trace);
        return dispatched;
    }

    public Map<String, Object> getRehabDispatchTrace(Long patientId, String planId) {
        if (patientId == null || planId == null || planId.trim().isEmpty()) {
            return new HashMap<>();
        }
        Map<String, Object> trace = rehabDispatchTraceStore.get(buildTraceKey(patientId, planId));
        return trace == null ? new HashMap<String, Object>() : trace;
    }

    public Object healthReportDaily(Long patientId, String scene) {
        String key = "report:daily:" + patientId + ":" + normalizeScene(scene);
        return getOrLoadCache(key, () -> post("/ai/health-report/daily", baseReq(patientId, scene), reportTimeoutMs));
    }

    public Object healthReportWeekly(Long patientId, String scene) {
        String key = "report:weekly:" + patientId + ":" + normalizeScene(scene);
        return getOrLoadCache(key, () -> post("/ai/health-report/weekly", baseReq(patientId, scene), reportTimeoutMs));
    }

    public Object healthReportMonthly(Long patientId, String scene) {
        String key = "report:monthly:" + patientId + ":" + normalizeScene(scene);
        return getOrLoadCache(key, () -> post("/ai/health-report/monthly", baseReq(patientId, scene), reportTimeoutMs));
    }

    public boolean isPatientSupported(Long patientId) {
        try {
            String key = "patient:supported:" + patientId;
            getOrLoadCache(key, () -> {
                post("/ai/risk/predict", baseReq(patientId, "doctor"));
                return Boolean.TRUE;
            });
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private Object getOrLoadCache(String key, Supplier<Object> loader) {
        long now = System.currentTimeMillis();
        CacheEntry entry = responseCache.get(key);
        if (entry != null && !entry.isExpired(now)) {
            return deepCopy(entry.data);
        }

        Object loaded;
        try {
            loaded = loader.get();
        } catch (Exception ex) {
            if (entry != null && entry.data != null) {
                return deepCopy(entry.data);
            }
            throw ex;
        }
        long ttl = Math.max(1000L, cacheTtlMs);
        responseCache.put(key, new CacheEntry(deepCopy(loaded), now + ttl));
        return loaded;
    }

    private void evictPatientCache(Long patientId) {
        if (patientId == null) {
            return;
        }
        String marker = ":" + patientId + ":";
        responseCache.keySet().removeIf(key -> key.contains(marker));
    }

    private String normalizeScene(String scene) {
        return (scene == null || scene.trim().isEmpty()) ? "patient" : scene.trim();
    }

    private String normalizePlanId(String planId) {
        return (planId == null || planId.trim().isEmpty()) ? "latest" : planId.trim();
    }

    private Object deepCopy(Object value) {
        if (value == null) {
            return null;
        }
        return JSON.parse(JSON.toJSONString(value));
    }

    private Map<String, Object> baseReq(Long patientId, String scene) {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", String.valueOf(patientId));
        req.put("scene", (scene == null || scene.trim().isEmpty()) ? "patient" : scene);
        req.put("source", "ruoyi");
        return req;
    }

    private String buildTraceKey(Long patientId, String planId) {
        return String.valueOf(patientId) + "::" + (planId == null ? "" : planId.trim());
    }

    private JSONObject toJsonObject(Object raw) {
        if (raw instanceof JSONObject) {
            return (JSONObject) raw;
        }
        if (raw == null) {
            return new JSONObject();
        }
        return JSONObject.parseObject(JSON.toJSONString(raw));
    }

    private String stringValue(Object value, String defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        String text = String.valueOf(value).trim();
        return text.isEmpty() ? defaultValue : text;
    }

    private Object post(String path, Map<String, Object> req) {
        return post(path, req, timeoutMs);
    }

    private Object post(String path, Map<String, Object> req, int requestTimeoutMs) {
        String url = baseUrl + path;
        HttpResponse response = HttpRequest.post(url)
                .timeout(requestTimeoutMs)
                .header("Content-Type", "application/json")
                .body(JSON.toJSONString(req))
                .execute();

        if (response.getStatus() < 200 || response.getStatus() >= 300) {
            throw new RuntimeException("AI service HTTP error: " + response.getStatus() + ", url=" + url);
        }

        JSONObject obj = JSON.parseObject(response.body());
        Integer code = obj.getInteger("code");
        if (code == null || code != 200) {
            throw new RuntimeException("AI service biz error: " + obj.getString("msg"));
        }
        return obj.get("data");
    }
}
