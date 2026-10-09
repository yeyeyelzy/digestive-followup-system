package com.ruoyi.web.controller.system;

import java.time.LocalDate;
import java.time.Period;
import java.util.List;
import java.util.Map;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.utils.StringUtils;
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
     * 患者端更新个人资料。
     */
    @PutMapping("/profile")
    public AjaxResult updateMyProfile(@RequestBody Map<String, Object> body)
    {
        LoginUser loginUser = getLoginUser();
        if (loginUser == null || loginUser.getUserId() == null)
        {
            return AjaxResult.error(401, "未登录或登录已过期");
        }

        Patient patient = new Patient();
        patient.setPatientId(loginUser.getUserId());

        Object phoneNumber = body.get("phoneNumber");
        if (phoneNumber != null)
        {
            String phone = String.valueOf(phoneNumber).trim();
            if (!phone.matches("^\\d{11}$"))
            {
                return AjaxResult.error("手机号格式错误");
            }
            patient.setPhoneNumber(phone);
        }

        Object gender = body.get("gender");
        if (gender != null && StringUtils.isNotEmpty(String.valueOf(gender)))
        {
            patient.setGender(Long.valueOf(String.valueOf(gender)));
        }

        Object weight = body.get("weight");
        if (weight != null && StringUtils.isNotEmpty(String.valueOf(weight)))
        {
            patient.setWeight(Long.valueOf(Math.round(Double.parseDouble(String.valueOf(weight)))));
        }

        Object avatarUrl = body.get("avatarUrl");
        if (avatarUrl != null)
        {
            patient.setAvatarUrl(String.valueOf(avatarUrl));
        }

        Object birthday = body.get("birthday");
        if (birthday != null && StringUtils.isNotEmpty(String.valueOf(birthday)))
        {
            try
            {
                LocalDate birth = LocalDate.parse(String.valueOf(birthday));
                int age = Period.between(birth, LocalDate.now()).getYears();
                if (age < 0)
                {
                    return AjaxResult.error("出生日期不能大于当前日期");
                }
                patient.setAge((long) age);
            }
            catch (Exception e)
            {
                return AjaxResult.error("出生日期格式错误");
            }
        }

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
}
