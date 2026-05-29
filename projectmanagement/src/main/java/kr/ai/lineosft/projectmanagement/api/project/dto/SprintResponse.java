package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Sprint;
import kr.ai.lineosft.projectmanagement.domain.project.entity.SprintStatus;
import lombok.Getter;

import java.time.LocalDate;

@Getter
public class SprintResponse {

    private final Long id;
    private final String name;
    private final String goal;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final SprintStatus status;
    private final Long projectId;

    public SprintResponse(Sprint sprint) {
        this.id = sprint.getId();
        this.name = sprint.getName();
        this.goal = sprint.getGoal();
        this.startDate = sprint.getStartDate();
        this.endDate = sprint.getEndDate();
        this.status = sprint.getStatus();
        this.projectId = sprint.getProject().getId();
    }
}
