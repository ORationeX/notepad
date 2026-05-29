package kr.ai.lineosft.projectmanagement.api.project.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectMethodology;
import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectStatus;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
public class ProjectRequest {

    @NotBlank(message = "프로젝트명은 필수 입력 항목입니다.")
    private String title;

    private String description;

    private ProjectStatus status;

    private ProjectMethodology methodology;

    @Min(0) @Max(100)
    private Integer progress;

    private LocalDate startDate;

    private LocalDate endDate;

    private List<Long> memberIds;
}
