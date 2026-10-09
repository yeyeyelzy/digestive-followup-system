package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
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
import com.ruoyi.system.domain.Doctor;
import com.ruoyi.system.service.IDoctorService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 医生管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/doctor")
public class DoctorController extends BaseController
{
    @Autowired
    private IDoctorService doctorService;

    /**
     * 查询医生管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:list')")
    @GetMapping("/list")
    public TableDataInfo list(Doctor doctor)
    {
        startPage();
        List<Doctor> list = doctorService.selectDoctorList(doctor);
        return getDataTable(list);
    }

    /**
     * 导出医生管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:export')")
    @Log(title = "医生管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Doctor doctor)
    {
        List<Doctor> list = doctorService.selectDoctorList(doctor);
        ExcelUtil<Doctor> util = new ExcelUtil<Doctor>(Doctor.class);
        util.exportExcel(response, list, "医生管理数据");
    }

    /**
     * 获取医生管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:query')")
    @GetMapping(value = "/{doctorId}")
    public AjaxResult getInfo(@PathVariable("doctorId") Long doctorId)
    {
        return success(doctorService.selectDoctorByDoctorId(doctorId));
    }

    /**
     * 新增医生管理
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:add')")
    @Log(title = "医生管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Doctor doctor)
    {
        return toAjax(doctorService.insertDoctor(doctor));
    }

    /**
     * 修改医生管理
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:edit')")
    @Log(title = "医生管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Doctor doctor)
    {
        return toAjax(doctorService.updateDoctor(doctor));
    }

    /**
     * 删除医生管理
     */
    @PreAuthorize("@ss.hasPermi('system:doctor:remove')")
    @Log(title = "医生管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{doctorIds}")
    public AjaxResult remove(@PathVariable Long[] doctorIds)
    {
        return toAjax(doctorService.deleteDoctorByDoctorIds(doctorIds));
    }
}
