package com.ruoyi.web.controller.system;

import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.baidu.aip.ocr.AipOcr;
import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.config.RuoYiConfig;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.utils.file.FileUploadUtils;
import com.ruoyi.common.utils.file.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
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
import com.ruoyi.system.domain.Discharge;
import com.ruoyi.system.service.IDischargeService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;
import org.springframework.web.multipart.MultipartFile;

/**
 * 出院小结管理Controller
 *
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/discharge")
public class DischargeController extends BaseController
{
    @Autowired
    private IDischargeService dischargeService;

    /**
     * 图片文字识别
     */
    @PostMapping("/ocr")
    public AjaxResult uploadFile(MultipartFile file) throws Exception
    {
        try
        {
            // 上传文件路径
            String filePath = RuoYiConfig.getUploadPath();
            // 上传并返回新文件名称
            String fileName = FileUploadUtils.upload(filePath, file);
            HashMap<String, String> options = new HashMap<String, String>();
            options.put("language_type", "CHN_ENG");//识别语言类型，默认为中英文混合
            options.put("detect_direction", "true");//是否检查图片朝向，默认false不检查
            options.put("detect_language", "true");//是否检查语言，默认false不检查
            options.put("probability", "true");//是否返回识别结果中每一行的置信度

            AipOcr aipOcr = new AipOcr("26910293", "Vas7C24ab2yV9dAOHPvwN231", "5yObSUwwbZbgO3Ea5vMGzf2lvoSDrFT9");
            // 调用接口，返回JSON格式数据
            JSONObject jsonObject = aipOcr.basicGeneral(file.getBytes(), options);
            //获取JSON对象里提取图片文字信息数组
            JSONArray jsonArray = jsonObject.getJSONArray("words_result");

            Discharge discharge = new Discharge();
            StringBuffer sb = new StringBuffer();
            for(int i = 0;i<jsonArray.length();i++){
                sb.append(jsonArray.getJSONObject(i).get("words"));
            }
            String words = sb.toString();
            String patientName = subString("姓名：","住院号：",words);
            discharge.setPatientName(patientName);

            String rysj = subString("入院日期","出院日期",words);

            SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
            discharge.setAdmissionDate(format.parse(rysj.substring(0,10)));

            String cysh = subString("出院日期","门诊诊断",words);
            discharge.setDischargeDate(format.parse(cysh.substring(0,10)));

            String dischargeDiagnosis = subString("出院诊断","入院情况",words);
            discharge.setDischargeDiagnosis(dischargeDiagnosis);
            String majorTestResult = subString("主要化验结果","打印",words);
            discharge.setMajorTestResult(majorTestResult);
            return success(discharge);
        }
        catch (Exception e)
        {
            return AjaxResult.error(e.getMessage());
        }
    }
    public String subString(String index,String end,String word){
        return word.substring(word.indexOf(index)+index.length(),word.indexOf(end));
    }

    /**
     * 查询出院小结管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:list')")
    @GetMapping("/list")
    public TableDataInfo list(Discharge discharge)
    {
        startPage();
        List<Discharge> list = dischargeService.selectDischargeList(discharge);
        return getDataTable(list);
    }

    /**
     * 【患者端】查询当前登录患者的出院小结列表
     */
    @GetMapping("/my-list")
    public AjaxResult myList()
    {
        LoginUser loginUser = getLoginUser();
        if (loginUser == null || loginUser.getUserId() == null)
        {
            return AjaxResult.error("用户未登录或用户信息获取失败");
        }

        Discharge queryParam = new Discharge();
        queryParam.setPatientId(loginUser.getUserId());
        List<Discharge> list = dischargeService.selectDischargeList(queryParam);
        return AjaxResult.success(list);
    }

    /**
     * 导出出院小结管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:export')")
    @Log(title = "出院小结管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Discharge discharge)
    {
        List<Discharge> list = dischargeService.selectDischargeList(discharge);
        ExcelUtil<Discharge> util = new ExcelUtil<Discharge>(Discharge.class);
        util.exportExcel(response, list, "出院小结管理数据");
    }

    /**
     * 获取出院小结管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:query')")
    @GetMapping(value = "/{admissionNumber}")
    public AjaxResult getInfo(@PathVariable("admissionNumber") Integer admissionNumber)
    {
        return success(dischargeService.selectDischargeByAdmissionNumber(admissionNumber));
    }

    /**
     * 新增出院小结管理
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:add')")
    @Log(title = "出院小结管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Discharge discharge)
    {
        return toAjax(dischargeService.insertDischarge(discharge));
    }

    /**
     * 修改出院小结管理
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:edit')")
    @Log(title = "出院小结管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Discharge discharge)
    {
        return toAjax(dischargeService.updateDischarge(discharge));
    }

    /**
     * 删除出院小结管理
     */
    @PreAuthorize("@ss.hasPermi('system:discharge:remove')")
    @Log(title = "出院小结管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{admissionNumbers}")
    public AjaxResult remove(@PathVariable Integer[] admissionNumbers)
    {
        return toAjax(dischargeService.deleteDischargeByAdmissionNumbers(admissionNumbers));
    }
}
