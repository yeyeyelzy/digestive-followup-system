package com.ruoyi.web.service.ai;

import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class RecoveryAchievementService {

    private static class State {
        int consecutiveHealthyDays;
        int totalHealthyDays;
        LocalDate lastDate;
        boolean lastHealthy;
    }

    private final Map<Long, State> stateMap = new ConcurrentHashMap<>();

    public Map<String, Object> buildCurrent(Long patientId, boolean healthyToday) {
        State s = stateMap.computeIfAbsent(patientId, k -> new State());
        LocalDate today = LocalDate.now();

        if (s.lastDate == null || !today.equals(s.lastDate)) {
            if (healthyToday) {
                s.totalHealthyDays += 1;
                if (s.lastDate != null && s.lastDate.plusDays(1).equals(today) && s.lastHealthy) {
                    s.consecutiveHealthyDays += 1;
                } else {
                    s.consecutiveHealthyDays = 1;
                }
            } else {
                s.consecutiveHealthyDays = 0;
            }
            s.lastDate = today;
            s.lastHealthy = healthyToday;
        }

        int titleId;
        String titleName;
        if (s.totalHealthyDays >= 60) {
            titleId = 4;
            titleName = "康复达人";
        } else if (s.totalHealthyDays >= 30) {
            titleId = 3;
            titleName = "康复进阶者";
        } else if (s.totalHealthyDays >= 7) {
            titleId = 2;
            titleName = "康复坚持者";
        } else {
            titleId = 1;
            titleName = "康复萌新";
        }

        int level = Math.min(10, 1 + s.totalHealthyDays / 7);

        Map<String, Object> data = new ConcurrentHashMap<>();
        data.put("current_title_id", titleId);
        data.put("current_title_name", titleName);
        data.put("current_level", level);
        data.put("consecutive_healthy_days", s.consecutiveHealthyDays);
        data.put("total_healthy_days", s.totalHealthyDays);
        data.put("healthy_today", healthyToday);
        return data;
    }
}
