package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.core.domain.entity.PatientUser;
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
import com.ruoyi.system.domain.Diet;
import com.ruoyi.system.service.IDietService;
import com.ruoyi.system.service.IPatientService;
import com.ruoyi.system.service.IPatientUserService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 饮食日记管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@RequestMapping("/system/diet")
public class DietController extends BaseController
{
    @Autowired
    private IDietService dietService;

    @Autowired
    private IPatientService patientService;

    @Autowired
    private IPatientUserService patientUserService;

    private boolean isPhoneLike(String value)
    {
        return value != null && value.matches("^\\d{11}$");
    }

    private String resolvePatientName(LoginUser loginUser)
    {
        Long patientId = loginUser.getUserId();
        String username = loginUser.getUsername();

        Patient patient = patientService.selectPatientByPatientId(patientId);
        if (patient != null && StringUtils.isNotEmpty(patient.getPatientName()) && !isPhoneLike(patient.getPatientName()))
        {
            return patient.getPatientName();
        }

        PatientUser patientUser = patientUserService.selectPatientUserByPatientId(patientId);
        if (patientUser == null && StringUtils.isNotEmpty(username))
        {
            patientUser = patientUserService.selectPatientUserByPhonenumber(username);
        }
        if (patientUser != null && StringUtils.isNotEmpty(patientUser.getPatientName()))
        {
            return patientUser.getPatientName();
        }

        return username;
    }

    /**
     * 查询饮食日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:diet:list')")
    @GetMapping("/list")
    public TableDataInfo list(Diet diet)
    {
        startPage();
        List<Diet> list = dietService.selectDietList(diet);
        return getDataTable(list);
    }

    /**
     * 查询当前登录患者的饮食日记列表
     */
    @GetMapping("/my-list")
    public TableDataInfo myList(Diet diet)
    {
        Long unifiedPatientId = getLoginUser().getUserId();
        diet.setPatientId(unifiedPatientId);
        startPage();
        List<Diet> list = dietService.selectDietList(diet);
        return getDataTable(list);
    }

    /**
     * 导出饮食日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:diet:export')")
    @Log(title = "饮食日记管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Diet diet)
    {
        List<Diet> list = dietService.selectDietList(diet);
        ExcelUtil<Diet> util = new ExcelUtil<Diet>(Diet.class);
        util.exportExcel(response, list, "饮食日记管理数据");
    }

    /**
     * 获取饮食日记管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:diet:query')")
    @GetMapping(value = "/{dietId}")
    public AjaxResult getInfo(@PathVariable("dietId") Long dietId)
    {
        return success(dietService.selectDietByDietId(dietId));
    }

    /**
     * 新增饮食日记管理
     */
    @Log(title = "饮食日记管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Diet diet)
    {
        LoginUser loginUser = getLoginUser();
        diet.setPatientId(loginUser.getUserId());
        diet.setPatientName(resolvePatientName(loginUser));
        if (dietService.searchByIdDate(diet).size() == 0)
            return toAjax(dietService.insertDiet(diet));
        else
            return toAjax(dietService.updateIdDate(diet));
    }

    /**
     * 修改饮食日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:diet:edit')")
    @Log(title = "饮食日记管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Diet diet)
    {
        if (!getLoginUser().getUserId().equals(diet.getPatientId())) {
            return AjaxResult.error("无权修改非本人的记录");
        }
        return toAjax(dietService.updateDiet(diet));
    }

    /**
     * 删除饮食日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:diet:remove')")
    @Log(title = "饮食日记管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{dietIds}")
    public AjaxResult remove(@PathVariable Long[] dietIds)
    {
        return toAjax(dietService.deleteDietByDietIds(dietIds));
    }
}
