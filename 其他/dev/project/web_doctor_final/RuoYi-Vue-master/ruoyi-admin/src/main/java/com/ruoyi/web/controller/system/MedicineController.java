package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.model.LoginUser;
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
import com.ruoyi.system.domain.Medicine;
import com.ruoyi.system.service.IMedicineService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 服药日记管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
//@Anonymous
@RequestMapping("/system/medicine")
public class MedicineController extends BaseController
{
    @Autowired
    private IMedicineService medicineService;

    /**
     * 查询服药日记管理列表
     */
//    @PreAuthorize("@ss.hasPermi('system:medicine:list')")
    @GetMapping("/list")
    public TableDataInfo list(Medicine medicine)
    {
        startPage();
        List<Medicine> list = medicineService.selectMedicineList(medicine);
        return getDataTable(list);
    }

    /**
     * 查询当前登录患者的服药日记列表
     */
    @GetMapping("/my-list")
    public TableDataInfo myList(Medicine medicine)
    {
        Long unifiedPatientId = getLoginUser().getUserId();
        medicine.setPatientId(unifiedPatientId);
        startPage();
        List<Medicine> list = medicineService.selectMedicineList(medicine);
        return getDataTable(list);
    }

    /**
     * 导出服药日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:medicine:export')")
    @Log(title = "服药日记管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Medicine medicine)
    {
        List<Medicine> list = medicineService.selectMedicineList(medicine);
        ExcelUtil<Medicine> util = new ExcelUtil<Medicine>(Medicine.class);
        util.exportExcel(response, list, "服药日记管理数据");
    }

    /**
     * 获取服药日记管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:medicine:query')")
    @GetMapping(value = "/{medicineId}")
    public AjaxResult getInfo(@PathVariable("medicineId") Long medicineId)
    {
        return success(medicineService.selectMedicineByMedicineId(medicineId));
    }

    /**
     * 新增服药日记管理
     */
//    @PreAuthorize("@ss.hasPermi('system:medicine:add')")
    @Log(title = "服药日记管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Medicine medicine)
    {
        // 1. 获取当前登录用户
        LoginUser loginUser = getLoginUser();

        // 2. 【核心】获取统一的 Long ID 和 Patient Name
        Long unifiedPatientId = loginUser.getUserId();
        String patientName = loginUser.getUsername();
        // 3. 设置新增记录的 patientId 和 patientName
        medicine.setPatientId(unifiedPatientId);
        medicine.setPatientName(patientName);
        if (medicineService.searchByIdDate(medicine).size() == 0)
            return toAjax(medicineService.insertMedicine(medicine));
        else
            return toAjax(medicineService.updateIdDate(medicine));
    }

    /**
     * 修改服药日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:medicine:edit')")
    @Log(title = "服药日记管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Medicine medicine)
    {
        if (!getLoginUser().getUserId().equals(medicine.getPatientId())) {
            return AjaxResult.error("无权修改非本人的记录");
        }
        return toAjax(medicineService.updateMedicine(medicine));
    }

    /**
     * 删除服药日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:medicine:remove')")
    @Log(title = "服药日记管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{medicineIds}")
    public AjaxResult remove(@PathVariable Long[] medicineIds)
    {
        return toAjax(medicineService.deleteMedicineByMedicineIds(medicineIds));
    }
}
