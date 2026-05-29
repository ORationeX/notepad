package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Phase;
import lombok.Getter;

import java.time.LocalDate;

@Getter
public class PhaseResponse {

    private final Long id;
    private final String name;
    private final String description;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final Integer progress;
    private final Long projectId;

    public PhaseResponse(Phase phase) {
        this.id = phase.getId();
        this.name = phase.getName();
        this.description = phase.getDescription();
        this.startDate = phase.getStartDate();
        this.endDate = phase.getEndDate();
        this.progress = phase.getProgress();
        this.projectId = phase.getProject().getId();
    }
}
