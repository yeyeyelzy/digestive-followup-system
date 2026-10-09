package com.ruoyi.web.controller.system;

import java.util.HashMap;
import java.util.List;
import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysFamily;
import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.core.domain.model.LoginBody;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.framework.web.service.FamilyLoginService;
import com.ruoyi.system.service.ISysFamilyService;
import com.ruoyi.system.service.ISysPatientFamilyService;
import com.ruoyi.system.service.IPatientUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.Diet;
import com.ruoyi.system.domain.Behavior;
import com.ruoyi.system.domain.Living;
import com.ruoyi.system.domain.Medicine;
import com.ruoyi.system.domain.Discharge;
import com.ruoyi.system.domain.Recovery;
import com.ruoyi.system.service.IDietService;
import com.ruoyi.system.service.IBehaviorService;
import com.ruoyi.system.service.ILivingService;
import com.ruoyi.system.service.IMedicineService;
import com.ruoyi.system.service.IDischargeService;
import com.ruoyi.system.service.IRecoveryService;
import java.util.ArrayList;
import java.util.Date;
// Add other services as needed

/**
 * 家属端 API Controller
 *
 * @author ruoyi
 */
@RestController
@RequestMapping("/api/family")
public class FamilyUserController extends BaseController
{
    @Autowired
    private FamilyLoginService familyLoginService;

    @Autowired
    private ISysFamilyService sysFamilyService;

    @Autowired
    private ISysPatientFamilyService sysPatientFamilyService;
    
    @Autowired
    private IPatientUserService patientUserService;

    @Autowired
    private IMedicineService medicineService;

    @Autowired
    private IDietService dietService;

    @Autowired
    private IBehaviorService behaviorService;

    @Autowired
    private ILivingService livingService;

    @Autowired
    private IDischargeService dischargeService;

    @Autowired
    private IRecoveryService recoveryService;
    
    // 登录
    @Anonymous
    @PostMapping("/login")
    public AjaxResult login(@RequestBody LoginBody loginBody) {
        String token = familyLoginService.login(loginBody.getUsername(), loginBody.getPassword());
        HashMap<String, String> result = new HashMap<>();
        result.put("token", token);
        return AjaxResult.success(result);
    }

    // 注册
    @Anonymous
    @PostMapping("/register")
    public AjaxResult register(@RequestBody SysFamily sysFamily) {
        boolean result = sysFamilyService.registerFamily(sysFamily);
        if (result) {
            return AjaxResult.success("注册成功");
        }
        return AjaxResult.error("注册失败，该手机号可能已存在");
    }

    // 获取个人信息
    @GetMapping("/profile")
    public AjaxResult getProfile() {
        LoginUser loginUser = getLoginUser();
        Long familyId = loginUser.getUserId();
        SysFamily family = sysFamilyService.selectSysFamilyByFamilyId(familyId);
        if (family == null) {
            return AjaxResult.error("用户不存在");
        }
        family.setPassword(null); 
        return AjaxResult.success(family);
    }

    @GetMapping("/getInfo")
    public AjaxResult getInfo() {
        return getProfile();
    }
    
    // 修改个人信息
    @PostMapping("/profile")
    public AjaxResult updateProfile(@RequestBody SysFamily sysFamily) {
        LoginUser loginUser = getLoginUser();
        sysFamily.setFamilyId(loginUser.getUserId());
        return toAjax(sysFamilyService.updateSysFamily(sysFamily));
    }

    /**
     * 绑定患者
     * 参数: patientPhone, patientName, relationship
     */
    @PostMapping("/bind")
    public AjaxResult bindPatient(@RequestBody HashMap<String, String> params) {
        String patientPhone = params.get("patientPhone");
        String relationship = params.get("relationship");
        
        // 1. 查找患者
        PatientUser patient = patientUserService.selectPatientUserByPhonenumber(patientPhone);
        if (patient == null) {
            return AjaxResult.error("未找到对应手机号的患者");
        }
        
        // 2. 绑定
        Long familyId = getLoginUser().getUserId();
        boolean result = sysPatientFamilyService.bindPatient(familyId, patient.getPatientId(), relationship);
        
        if (result) {
            return AjaxResult.success("绑定成功");
        } else {
            return AjaxResult.error("绑定失败，可能已经绑定过");
        }
    }

    // 解绑
    @PostMapping("/unbind")
    public AjaxResult unbindPatient(@RequestBody HashMap<String, Long> params) {
        Long patientId = params.get("patientId");
        Long familyId = getLoginUser().getUserId();
        return toAjax(sysPatientFamilyService.unbindPatient(familyId, patientId));
    }

    // 获取已绑定患者列表
    @GetMapping("/patients")
    public AjaxResult getBoundPatients() {
        Long familyId = getLoginUser().getUserId();
        List<PatientUser> list = sysPatientFamilyService.selectBoundPatientsByFamilyId(familyId);
        return AjaxResult.success(list);
    }

    // === 患者数据查询接口 (带权限校验) ===

    /**
     * 查询患者服药记录
     */
    @GetMapping("/patient/medicine")
    public TableDataInfo getPatientMedicine(Medicine medicine) {
        Long patientId = medicine.getPatientId();
        if (patientId == null) {
            return getDataTable(java.util.Collections.emptyList());
        }

        if (!sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return getDataTable(java.util.Collections.emptyList());
        }
        
        startPage();
        List<Medicine> list = medicineService.selectMedicineList(medicine);
        return getDataTable(list);
    }

    @GetMapping("/patient/diet")
    public TableDataInfo getPatientDiet(Diet diet) {
        Long patientId = diet.getPatientId();
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return getDataTable(java.util.Collections.emptyList());
        }

        startPage();
        return getDataTable(dietService.selectDietList(diet));
    }

    @GetMapping("/patient/behavior")
    public TableDataInfo getPatientBehavior(Behavior behavior) {
        Long patientId = behavior.getPatientId();
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return getDataTable(java.util.Collections.emptyList());
        }

        startPage();
        return getDataTable(behaviorService.selectBehaviorList(behavior));
    }

    @GetMapping("/patient/living")
    public TableDataInfo getPatientLiving(Living living) {
        Long patientId = living.getPatientId();
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return getDataTable(java.util.Collections.emptyList());
        }

        startPage();
        return getDataTable(livingService.selectLivingList(living));
    }

    @GetMapping("/patient/discharge")
    public AjaxResult getPatientDischarge(Discharge discharge) {
        Long patientId = discharge.getPatientId();
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return AjaxResult.success(java.util.Collections.emptyList());
        }

        return AjaxResult.success(dischargeService.selectDischargeList(discharge));
    }

    @GetMapping("/patient/recovery")
    public AjaxResult getPatientRecovery(Recovery recovery) {
        Long patientId = recovery.getPatientId();
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return AjaxResult.success(java.util.Collections.emptyList());
        }

        return AjaxResult.success(recoveryService.selectRecoveryList(recovery));
    }

    @GetMapping("/patient/visual/{patientId}")
    public AjaxResult getPatientVisual(@PathVariable Long patientId) {
        if (patientId == null || !sysPatientFamilyService.isBound(getLoginUser().getUserId(), patientId)) {
            return AjaxResult.success(new HashMap<>());
        }

        Recovery query = new Recovery();
        query.setPatientId(patientId);
        List<Recovery> list = recoveryService.selectRecoveryList(query);

        List<Date> dayList = new ArrayList<>();
        List<Long> NtProbnpList = new ArrayList<>();
        List<Long> LVEFList = new ArrayList<>();
        List<Long> CPET1List = new ArrayList<>();
        List<Long> CPET2List = new ArrayList<>();
        List<Long> PeakBloodPressureList = new ArrayList<>();
        List<Long> PpeakHeartRateList = new ArrayList<>();
        List<Long> AnaerobicThresholdBloodPressureList = new ArrayList<>();
        List<Long> AnaerobicThresholdHeartRateList = new ArrayList<>();

        for (Recovery recovery : list) {
            dayList.add(recovery.getDate());
            NtProbnpList.add(recovery.getNtProbnp());
            LVEFList.add(recovery.getLVEF());
            CPET1List.add(recovery.getCPET1());
            CPET2List.add(recovery.getCPET2());
            PeakBloodPressureList.add(recovery.getPeakBloodPressure());
            PpeakHeartRateList.add(recovery.getPeakHeartRate());
            AnaerobicThresholdBloodPressureList.add(recovery.getAnaerobicThresholdBloodPressure());
            AnaerobicThresholdHeartRateList.add(recovery.getAnaerobicThresholdHeartRate());
        }

        HashMap<String, Object> map = new HashMap<>();
        map.put("dayList", dayList);
        map.put("NtProbnpList", NtProbnpList);
        map.put("LVEFList", LVEFList);
        map.put("CPET1List", CPET1List);
        map.put("CPET2List", CPET2List);
        map.put("PeakBloodPressureList", PeakBloodPressureList);
        map.put("PpeakHeartRateList", PpeakHeartRateList);
        map.put("AnaerobicThresholdBloodPressureList", AnaerobicThresholdBloodPressureList);
        map.put("AnaerobicThresholdHeartRateList", AnaerobicThresholdHeartRateList);
        return AjaxResult.success(map);
    }
}
