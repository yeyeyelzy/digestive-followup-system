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
import com.ruoyi.system.domain.Living;
import com.ruoyi.system.domain.Patient;
import com.ruoyi.system.service.ILivingService;
import com.ruoyi.system.service.IPatientService;
import com.ruoyi.system.service.IPatientUserService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 生活方式日记管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@RequestMapping("/system/living")
public class LivingController extends BaseController
{
    @Autowired
    private ILivingService livingService;

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
     * 查询生活方式日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:living:list')")
    @GetMapping("/list")
    public TableDataInfo list(Living living)
    {
        startPage();
        List<Living> list = livingService.selectLivingList(living);
        return getDataTable(list);
    }

    /**
     * 查询当前登录患者的生活方式日记列表
     */
    @GetMapping("/my-list")
    public TableDataInfo myList(Living living)
    {
        Long unifiedPatientId = getLoginUser().getUserId();
        living.setPatientId(unifiedPatientId);
        startPage();
        List<Living> list = livingService.selectLivingList(living);
        return getDataTable(list);
    }

    /**
     * 导出生活方式日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:living:export')")
    @Log(title = "生活方式日记管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Living living)
    {
        List<Living> list = livingService.selectLivingList(living);
        ExcelUtil<Living> util = new ExcelUtil<Living>(Living.class);
        util.exportExcel(response, list, "生活方式日记管理数据");
    }

    /**
     * 获取生活方式日记管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:living:query')")
    @GetMapping(value = "/{livingId}")
    public AjaxResult getInfo(@PathVariable("livingId") Long livingId)
    {
        return success(livingService.selectLivingByLivingId(livingId));
    }

    /**
     * 新增生活方式日记管理
     */
    @Log(title = "生活方式日记管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Living living)
    {
        LoginUser loginUser = getLoginUser();
        living.setPatientId(loginUser.getUserId());
        living.setPatientName(resolvePatientName(loginUser));
        if (livingService.searchByIdDate(living).size() == 0)
            return toAjax(livingService.insertLiving(living));
        else
            return toAjax(livingService.updateIdDate(living));
    }

    /**
     * 修改生活方式日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:living:edit')")
    @Log(title = "生活方式日记管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Living living)
    {
        if (!getLoginUser().getUserId().equals(living.getPatientId())) {
            return AjaxResult.error("无权修改非本人的记录");
        }
        return toAjax(livingService.updateLiving(living));
    }

    /**
     * 删除生活方式日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:living:remove')")
    @Log(title = "生活方式日记管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{livingIds}")
    public AjaxResult remove(@PathVariable Long[] livingIds)
    {
        return toAjax(livingService.deleteLivingByLivingIds(livingIds));
    }
}
