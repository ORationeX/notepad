package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface RequirementCategoryRepository extends JpaRepository<RequirementCategory, Long> {

    @Query("SELECT c FROM RequirementCategory c WHERE c.project.id = :projectId OR c.project IS NULL ORDER BY c.id ASC")
    List<RequirementCategory> findByProjectIdOrGlobal(@Param("projectId") Long projectId);
}
