package com.ruoyi.web.controller.system;

import java.util.Date;
import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.dto.PatientProfileForm;
import com.ruoyi.common.utils.SecurityUtils;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.service.IPatientService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 患者管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/patient")
public class PatientController extends BaseController
{
    @Autowired
    private IPatientService patientService;

    /**
     * 查询患者管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:patient:list')")
    @GetMapping("/list")
    public TableDataInfo list(Patient patient)
    {
        startPage();
        List<Patient> list = patientService.selectPatientList(patient);
        return getDataTable(list);
    }

    /**
     * 导出患者管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:patient:export')")
    @Log(title = "患者管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Patient patient)
    {
        List<Patient> list = patientService.selectPatientList(patient);
        ExcelUtil<Patient> util = new ExcelUtil<Patient>(Patient.class);
        util.exportExcel(response, list, "患者管理数据");
    }

    /**
     * 获取患者管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:patient:query')")
    @GetMapping(value = "/{patientId}")
    public AjaxResult getInfo(@PathVariable("patientId") Long patientId)
    {
        return success(patientService.selectPatientByPatientId(patientId));
    }

    /**
     * 新增患者管理
     */
    @PreAuthorize("@ss.hasPermi('system:patient:add')")
    @Log(title = "患者管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Patient patient)
    {
        return toAjax(patientService.insertPatient(patient));
    }

    /**
     * 修改患者管理
     */
    @PreAuthorize("@ss.hasPermi('system:patient:edit')")
    @Log(title = "患者管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Patient patient)
    {
        return toAjax(patientService.updatePatient(patient));
    }

    /**
     * 删除患者管理
     */
    @PreAuthorize("@ss.hasPermi('system:patient:remove')")
    @Log(title = "患者管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{patientIds}")
    public AjaxResult remove(@PathVariable Long[] patientIds)
    {
        return toAjax(patientService.deletePatientByPatientIds(patientIds));
    }

    /**
     * 【新增接口：更新患者个人资料】
     * 接口路径：PUT /system/patient/profile
     */
    @PutMapping("/profile")
    public AjaxResult updatePatientProfile(@RequestBody PatientProfileForm form) // 【使用 DTO】
    {
        // 1. 获取当前登录用户的 ID
        Long currentPatientId = SecurityUtils.getUserId(); // 假设 SecurityUtils 能获取当前登录ID
        if (currentPatientId == null || currentPatientId == 0) {
            return AjaxResult.error("用户未登录或ID无效");
        }

        // 2. 调用唯一的 Service 入口方法
        int rows = patientService.updatePatientProfile(currentPatientId, form);

        return rows > 0 ? AjaxResult.success("个人信息修改成功") : AjaxResult.error("个人信息修改失败");
    }
}
