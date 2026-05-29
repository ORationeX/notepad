package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.common.entity.BaseTimeEntity;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "phases")
public class Phase extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(length = 1000)
    private String description;

    private LocalDate startDate;

    private LocalDate endDate;

    @Column(nullable = false)
    private Integer progress;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @Builder
    private Phase(String name, String description, LocalDate startDate, LocalDate endDate, Integer progress, Project project) {
        this.name = name;
        this.description = description;
        this.startDate = startDate;
        this.endDate = endDate;
        this.progress = progress != null ? progress : 0;
        this.project = project;
    }

    public void update(String name, String description, LocalDate startDate, LocalDate endDate, Integer progress) {
        this.name = name;
        this.description = description;
        this.startDate = startDate;
        this.endDate = endDate;
        if (progress != null) {
            this.progress = progress;
        }
    }
}
